#Proceduaraly Generated Terrain!
#15-112 Final Project

#by James Muir
#anderw id: jmuir

#test mode toggle
test = False

#openGL code heavily inspired by Leonhard Vogt's tutorial

import sys
import warnings
import pyglet
pyglet.options['debug_gl'] = False
from pyglet.gl import *
from pyglet.window import key
import ctypes
from noise import *

#I wrote lib3d
from lib3d import *
#I also wrote scene3d
from scene3d import *

#all of the rendering stuff:

renderProgram = None
copyProgram = None
framebuffer = None
window = None

#converts gl type names to their actual instances
TYPE_NAME_TO_TYPE = {
	GL_FLOAT: GLfloat,
	GL_DOUBLE: GLdouble,
	GL_INT: GLint,
	GL_UNSIGNED_INT: GLuint,
	GL_BYTE: GLbyte,
	GL_UNSIGNED_BYTE: GLubyte,
	GL_SHORT: GLshort,
	GL_UNSIGNED_SHORT: GLushort,
}

#compiles a glsl shader
def compileShader(shaderType, shaderSource):
	# compiles a shader
	shaderName = glCreateShader(shaderType)
	srcBuffer = ctypes.create_string_buffer(shaderSource)
	bufPointer = ctypes.cast(ctypes.pointer(ctypes.pointer(srcBuffer)),\
	 ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
	length = ctypes.c_int(len(shaderSource) + 1)
	glShaderSource(shaderName, 1, bufPointer, ctypes.byref(length))
	glCompileShader(shaderName)

	#error log
	success = GLint(0)
	glGetShaderiv(shaderName, GL_COMPILE_STATUS, ctypes.byref(success))

	length = GLint(0)
	glGetShaderiv(shaderName, GL_INFO_LOG_LENGTH, ctypes.byref(length))
	logBuffer = ctypes.create_string_buffer(length.value)
	glGetShaderInfoLog(shaderName, length, None, logBuffer)

	#print errors
	logMessage = logBuffer.value[:length.value].decode("ascii").strip()
	if logMessage:
		sys.stderr.write(logMessage + "\n")

	if not success:
		raise ValueError("Compiling of shader failed.")

	return shaderName

def linkProgram(programName):
	#links a glsl (shader) program

	glLinkProgram(programName)

	#error checking:

	success = GLint(0)
	glGetProgramiv(programName, GL_LINK_STATUS, ctypes.byref(success))

	length = GLint(0)
	glGetProgramiv(programName, GL_INFO_LOG_LENGTH, ctypes.byref(length))
	logBuffer = ctypes.create_string_buffer(length.value)
	glGetProgramInfoLog(programName, length, None, logBuffer)

	logMessage = logBuffer.value[:length.value].decode("ascii").strip()
	if logMessage:
		sys.stderr.write(logMessage + "\n")

	if not success:
		raise ValueError("Linking the shader failed.")

# a glsl shader program
# a shader program takes in vertices and returns pixels onscreen, essentially
class shaderProgram:
	def __init__(self, vertexShader, fragmentShader, attributes):
		#compile and link shaders
		self.programName = glCreateProgram()
		glAttachShader(self.programName, \
			compileShader(GL_VERTEX_SHADER, vertexShader))
		glAttachShader(self.programName, \
			compileShader(GL_FRAGMENT_SHADER, fragmentShader))
		linkProgram(self.programName)

		#vertex type
		#you can store lots of things in a vertex buffer objects
		#including normals and colors as well as verticies
		class VERTEX(ctypes.Structure):
			_fields_ = [ (name, TYPE_NAME_TO_TYPE[tname]*size)
			for (name, tname, size) in attributes ]

		self.VERTEX = VERTEX
		#generates vertex buffers and arrays
		self.vertexArrayName = GLuint(0)
		self.vertexBufferName = GLuint(0)
		glGenVertexArrays(1, ctypes.byref(self.vertexArrayName))
		glGenBuffers(1, ctypes.byref(self.vertexBufferName))
		#generates vertex arrays
		glBindVertexArray(self.vertexArrayName)
		glBindBuffer(GL_ARRAY_BUFFER, self.vertexBufferName)
		for (name, tname, size) in attributes:
			location = glGetAttribLocation(self.programName, \
				ctypes.create_string_buffer(name.encode("ascii")))
			if location <0:
				warnings.warn("Atrribute %r is not present." %name, stacklevel = 2)
				continue
			glEnableVertexAttribArray(location)
			glVertexAttribPointer(location, size, tname, False,
								ctypes.sizeof(VERTEX),
								ctypes.c_void_p(getattr(VERTEX, name).offset))
		glBindVertexArray(0)
		glBindBuffer(GL_ARRAY_BUFFER, 0)
	#so you can use with keyword
	def __enter__(self):
		glUseProgram(self.programName)
		glBindVertexArray(self.vertexArrayName)

	def __exit__(self, *unused):
		glUseProgram(0)
		glBindVertexArray(0)

	#for sending vertex info
	def sendData(self, data):
		data = (self.VERTEX * len(data))(*data)

		glBindBuffer(GL_ARRAY_BUFFER, self.vertexBufferName)
		glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(data), data, GL_DYNAMIC_DRAW)
		glBindBuffer(GL_ARRAY_BUFFER, 0)

def setupRender():
	#define the shaders

	#vertex shader transforms the vertices of the triangles
	vertexShader = b"""
		#330
		//VERTEX SHADER
        uniform mat4 projectionView;
        uniform mat4 model;
        uniform vec3 light;

        attribute vec3 position;
        attribute vec3 normal;
        attribute vec4 color;

        varying vec4 varColor;
        //finds angle between two vectors
        float angle(vec3 one, vec3 two)
        {
            return acos(dot(one, two) / (length(one) * length(two)));
        }

        void main()
        {
        	//sets screen coords of triangle vertices
            gl_Position = projectionView * model * vec4(position, 1.0);
            //directional lighting stuff
           	vec3 transformedNormal = vec3(model * vec4(normal, 1.0));
            float shade = angle(light, transformedNormal)/(acos(-1));
            varColor = color*shade;
            //varColor = color;
        }
	"""
	#sets colors of pixels
	fragmentShader = b"""
		#330
		//FRAGMENT SHADER
		varying vec4 varColor;

		void main()
		{
			gl_FragColor = varColor;
		}
	"""
	#position, normal, and color are passed to the shader program
	return shaderProgram(vertexShader, fragmentShader, [
		("position", GL_FLOAT, 3),
		("normal", GL_FLOAT, 3),
		("color", GL_FLOAT, 4)
		])


#uniforms are values that don't change between draw calls
def setUniforms(projectionView, model, light):
	with renderProgram:
		#set uniform matricies and light vector

		#projectionView matrix
		projectionView_list = list(projectionView.col0+projectionView.col1+\
			projectionView.col2+projectionView.col3)
		projectionView_list_ctype = (GLfloat*16)(*projectionView_list)
		projectionViewPos = glGetUniformLocation(renderProgram.programName, \
			b"projectionView")
		glUniformMatrix4fv(projectionViewPos,GLsizei(1),GL_FALSE,\
			projectionView_list_ctype)

		#model
		model_list = list(model.col0+model.col1+model.col2+model.col3)
		model_list_ctype = (GLfloat*16)(*model_list)
		modelPos = glGetUniformLocation(renderProgram.programName, b"model")
		glUniformMatrix4fv(modelPos,GLsizei(1),GL_FALSE,model_list_ctype)

		#light
		x = GLfloat(light.x)
		y = GLfloat(light.y)
		z = GLfloat(light.z)
		lightPos = glGetUniformLocation(renderProgram.programName, b"light")
		glUniform3f(lightPos,x,y,z)


#draws all of the models in a scene
def drawScene():
	#clear destination
	glClearColor(0.0,0.0,0.0,1.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	#draw all the models
	for model in scene.models:
		drawModel(model)

#draws a model
def drawModel(model):
	#set projectionView matrix
	projectionView = scene.camera.projectionMatrix() * scene.camera.viewMatrix()
	modelMatrix = model.modelMatrix()
	light = scene.light.direction
	setUniforms(projectionView, modelMatrix, light)
	data = []
	count = 0
	for shape in model.shapes:
		for triangle in shape.triangles:
			for point in triangle.points:
				data.append((tuple(point),tuple(triangle.normal),tuple(shape.color)))
				count += 1
	renderProgram.sendData(data)
	#draw using the vertex array for vertex information
	with renderProgram:
		#Draw!
		glDrawArrays(GL_TRIANGLES, 0, count)

#finds the color of a terrain triangle based on it's height (y) values
def heightColor(height):
	if height > .3/4:
				color = vec4(1.0,1.0,1.0,1.0)
	elif height>-.3/4:
		color = vec4(0.6,0.6,0.6,1.0)
	else:
		color = vec4(0,1,0,1)
	return color

#proceduarally generates terrain using simplex noise
def createTerrain(l,w,o,offsetx,offsetz):
	#the procedural generation of the terrain
	shapes = []
	for row in range(l):
		for col in range(w):
			#find the color based on the height
			a = snoise2(row+offsetx,col+offsetz,octaves = o)
			b = snoise2(row+1+offsetx,col+1+offsetz,octaves = o)
			c = snoise2(row+offsetx,col+1+offsetz,octaves = o)
			height = sum((a,b,c))/4
			color = heightColor(height)
			shapes.append(shape(color,
				[triangle([vec3(0+row+offsetx,a,0+col+offsetz),
					vec3(1+row+offsetx,b,1+col+offsetz),\
					vec3(0+row+offsetx,c,1+col+offsetz)])]))
			#find the color based on the height
			a = snoise2(row+1+offsetx,col+offsetz,octaves = o)
			b = snoise2(row+1+offsetx,col+1+offsetz,octaves = o)
			c = snoise2(row+offsetx,col+offsetz,octaves = o)
			height = sum((a,b,c))/4
			color = heightColor(height)
			shapes.append(shape(color,
					[triangle([vec3(1+row+offsetx,a,0+col+offsetz),\
						vec3(1+row+offsetx,b,1+col+offsetz),\
						vec3(0+row+offsetx,c,0+col+offsetz)])]))
	return shapes

#initializes a scene
def setUpScene():
	#set up the floor
	floorShapes = createTerrain(15,15,5,0,0)
	pos = vec3(0,0,0)
	rot = quat(1,0,0,0)
	scale = vec3(10,11,10)
	floor = model(pos,rot,scale,floorShapes)
	#set up a cube
	cubeShape = shape(vec4(1,0,0,1),
		[
		triangle([vec3(0,0,0),vec3(0,1,0),vec3(1,0,0)]),
		triangle([vec3(1,1,0),vec3(1,0,0),vec3(0,1,0)]),
		triangle([vec3(0,0,1),vec3(0,1,1),vec3(0,0,0)]),
		triangle([vec3(0,1,0),vec3(0,0,0),vec3(0,1,1)]),
		triangle([vec3(0,1,0),vec3(0,1,1),vec3(1,1,0)]),
		triangle([vec3(1,1,1),vec3(1,1,0),vec3(0,1,1)]),
		triangle([vec3(1,0,0),vec3(1,1,0),vec3(1,0,1)]),
		triangle([vec3(1,1,1),vec3(1,0,1),vec3(1,1,0)]),
		triangle([vec3(0,0,0),vec3(1,0,0),vec3(0,0,1)]),
		triangle([vec3(1,0,1),vec3(0,0,1),vec3(1,0,0)]),
		triangle([vec3(1,0,1),vec3(1,1,1),vec3(0,0,1)]),
		triangle([vec3(0,1,1),vec3(0,0,1),vec3(1,1,1)])
		])
	pos = vec3(-4,10,-4)
	rot = quat(1,0,0,0)
	scale = vec3(3,3,3)
	cube1 = model(pos,rot,scale,
		[
		cubeShape
		])
	#set up a cube
	cubeShape = shape(vec4(1,0,0,1),
		[
		triangle([vec3(0,0,0),vec3(0,1,0),vec3(1,0,0)]),
		triangle([vec3(1,1,0),vec3(1,0,0),vec3(0,1,0)]),
		triangle([vec3(0,0,1),vec3(0,1,1),vec3(0,0,0)]),
		triangle([vec3(0,1,0),vec3(0,0,0),vec3(0,1,1)]),
		triangle([vec3(0,1,0),vec3(0,1,1),vec3(1,1,0)]),
		triangle([vec3(1,1,1),vec3(1,1,0),vec3(0,1,1)]),
		triangle([vec3(1,0,0),vec3(1,1,0),vec3(1,0,1)]),
		triangle([vec3(1,1,1),vec3(1,0,1),vec3(1,1,0)]),
		triangle([vec3(0,0,0),vec3(1,0,0),vec3(0,0,1)]),
		triangle([vec3(1,0,1),vec3(0,0,1),vec3(1,0,0)]),
		triangle([vec3(1,0,1),vec3(1,1,1),vec3(0,0,1)]),
		triangle([vec3(0,1,1),vec3(0,0,1),vec3(1,1,1)])
		])
	pos = vec3(-4,2,-4)
	rot = quat(1,0,0,0)
	scale = vec3(3,3,3)
	cube2 = model(pos,rot,scale,
		[
		cubeShape
		])
	#set up light
	theLight = light(vec3(3,2,1))
	#set up the camera
	pos = vec3(-2,-5,-2)
	rot = makeRotationQuat(math.pi, unitvy)
	fov = 90
	aspectRatio = window.width/window.height
	nearClip = 1
	farClip = 100
	theCamera = camera(pos,rot,fov,aspectRatio,nearClip,farClip)
	#set up the scene
	theScene = scene([cube1,cube2,floor],theLight,theCamera)

	return theScene

#called every frame
def update(dt):
	#player movement
	s = 5
	if scene.data.updates.forward:
		scene.camera.move(vec3(0,0,1)*dt*s)
	if scene.data.updates.backward:
		scene.camera.move(vec3(0,0,-1)*dt*s)
	if scene.data.updates.left:
		scene.camera.move(vec3(1,0,0)*dt*s)
	if scene.data.updates.right:
		scene.camera.move(vec3(-1,0,0)*dt*s)
	if scene.data.updates.up:
		scene.camera.move(vec3(0,-1,0)*dt*s)
	if scene.data.updates.down:
		scene.camera.move(vec3(0,1,0)*dt*s)

	#controllable cube movement
	if scene.data.updates.cube0right:
		rotq = makeRotationQuat(math.pi/4*dt, unitvx)
		scene.models[0].rotate(rotq)
	if scene.data.updates.cube0left:
		rotq = makeRotationQuat(-math.pi/4*dt, unitvx)
		scene.models[0].rotate(rotq)
	if scene.data.updates.cube0up:
		rotq = makeRotationQuat(math.pi/4*dt, unitvy)
		scene.models[0].rotate(rotq)
	if scene.data.updates.cube0down:
		rotq = makeRotationQuat(-math.pi/4*dt, unitvy)
		scene.models[0].rotate(rotq)
	#renders everthing
	drawScene()

#initates game
def init():
	#makes a window
	global window
	window = pyglet.window.Window(fullscreen = True)
	window.set_exclusive_mouse(True)

	#makes a scene
	global scene
	scene = setUpScene()

	#for input
	scene.data.updates = Struct()
	scene.data.updates.forward = False
	scene.data.updates.backward = False
	scene.data.updates.left = False
	scene.data.updates.right = False
	scene.data.updates.cube0right = False
	scene.data.updates.cube0left= False
	scene.data.updates.cube0up = False
	scene.data.updates.cube0down = False
	scene.data.updates.up = False
	scene.data.updates.down = False


	#set up event handlers
	setUpEvents()

	#sets up renderer
	global renderProgram
	renderProgram = setupRender()

	#set the viewport
	glViewport(0,0,window.width,window.height)

	#enable zbuffer
	glEnable(GL_DEPTH_TEST)
	glDepthFunc(GL_LEQUAL)

	#set the framerate
	pyglet.clock.schedule_interval(update, 1/30)

#sets up event handlers
def setUpEvents():
	@window.event
	def on_key_press(symbol, modifiers):
		#moving cube
		if symbol == key.RIGHT:
			scene.data.updates.cube0right = True
		elif symbol == key.LEFT:
			scene.data.updates.cube0left = True
		elif symbol == key.UP:
			scene.data.updates.cube0up = True
		elif symbol == key.DOWN:
			scene.data.updates.cube0down = True
		#moving player
		elif symbol == key.W:
			scene.data.updates.forward = True
		elif symbol == key.S:
			scene.data.updates.backward = True
		elif symbol == key.A:
			scene.data.updates.left = True
		elif symbol == key.D:
			scene.data.updates.right = True
		elif symbol == key.LSHIFT:
			scene.data.updates.up = True
		elif symbol == key.LCTRL:
			scene.data.updates.down = True
	@window.event
	def on_key_release(symbol, modifiers):
		#moving cube
	    if symbol == key.RIGHT:
	    	scene.data.updates.cube0right = False
	    elif symbol == key.LEFT:
	    	scene.data.updates.cube0left = False
	    elif symbol == key.UP:
	    	scene.data.updates.cube0up = False
	    elif symbol == key.DOWN:
	    	scene.data.updates.cube0down = False
	    #moving player
	    elif symbol == key.W:
	    	scene.data.updates.forward = False
	    elif symbol == key.S:
	    	scene.data.updates.backward = False
	    elif symbol == key.A:
	    	scene.data.updates.left = False
	    elif symbol == key.D:
	    	scene.data.updates.right = False
	    elif symbol == key.LSHIFT:
	    	scene.data.updates.up = False
	    elif symbol == key.LCTRL:
	    	scene.data.updates.down = False
	#lets player look around
	@window.event
	def on_mouse_motion(x, y, dx, dy):
		qyaw = makeRotationQuat(-dx/100, unitvy)
		qpitch = makeRotationQuat(dy/100, unitvx)
		scene.camera.fps(qpitch,qyaw)
	#draws the scene after every event
	@window.event
	def on_draw():
		drawScene()

#starts program
def run():
	init()
	pyglet.app.run()

#test functions
def runTests():
	#how to use library to transform a point
	rotQuat1 = makeRotationQuat(math.pi/2, vec3(0,0,1))
	print(rotQuat1)
	rotQuat2 = makeRotationQuat(math.pi/2, vec3(1,0,0))
	print(rotQuat2)
	rotQuat3 = makeRotationQuat(-math.pi/2, vec3(0,1,0))
	print(rotQuat3)
	scale = makeScaleMatrix(vec3(2,0,0))
	trans = makeTranslationMatrix(vec3(1,0,0))
	proj = makeProjectionMatrix(math.pi/2,8/6,1,100)
	#1 first, then 2, then 3 are applied
	rotQuat = rotQuat3 * rotQuat2 * rotQuat1
	print(rotQuat)
	rot = makeQuatRotationMatrix(rotQuat)
	point = vec4(1,0,0,1)
	print(point)
	#note: scale is applied first, then rot, then trans
	newPoint = proj * trans * rot * scale * point
	print(newPoint)

#actually run the program
if test == True:
	runTests()
else:
	run()

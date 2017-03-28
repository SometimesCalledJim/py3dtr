#by James Muir

from lib3d import *

#a structure, you can stick stuff in it
class Struct:
	pass

#a scene, holds models, a camera, and a directional light
class scene:
	def __init__(self,models,light,camera):
		#models is a list of model objects
		self.models = models
		#light is a vec3
		self.light = light
		#camera is a camera object
		self.camera = camera
		self.data = Struct()

#a camera, stores position and rotation data as well as a projection matrix
class camera:
	def __init__(self,pos,rot,fov,aspectRatio,nearClip,farClip):
		#pos is a vec3
		self.pos = pos
		#rot is a rotation unit quaternion
		self.rot = rot
		#fov is a float or int of the vertical field of view
		self.fov = fov
		self.aspectRatio = aspectRatio
		#near and far clipping planes
		self.nearClip = nearClip
		self.farClip = farClip

	def move(self,direction):
		#direction is a vec3
		rot = self.rot
		newRot = quat(-rot.w,rot.x,rot.y,rot.z)
		v4 = makeQuatRotationMatrix(newRot) * vec4(direction.x,direction.y,\
			direction.z,1)
		self.pos = self.pos + vec3(v4.x,v4.y,v4.z)

	def rotate(self,rotation):
		#rotation is a rotation unit quaternion
		self.rot = rotation * self.rot

	#lets you make a first person shooter style camera
	def fps(self,qpitch,qyaw):
		self.rot = qyaw * self.rot * qpitch

	#updates the matrices
	def update(self):
		#update transform matrix
		translate = makeTranslationMatrix(self.pos)
		rotate = makeQuatRotationMatrix(self.rot)
		self.view = rotate * translate
		#update projectionMatrix
		self.projection = makeProjectionMatrix(self.fov,self.aspectRatio,\
			self.nearClip,self.farClip)

	#the viewMatrix, takes coordinates from world space to camera space
	def viewMatrix(self):
		self.update()
		return self.view

	#the projection matrix, takes coords from camera space
	# to screen space, also puts them in perspective
	def projectionMatrix(self):
		self.update()
		return self.projection

#a 3d model, has a position, a rotation, a scale, and component shapes
class model():
	def __init__(self,pos,rot,scale,shapes):
		#pos is a vec3
		self.pos = pos
		#rot is a rotation unit quaternion
		self.rot = rot
		#scale is a vec3
		self.scale = scale
		#shapes is a list of shape objects
		self.shapes = shapes

	def move(self,direction):
		#direction is a vec3
		self.pos = self.pos + direction

	def rotate(self,rotation):
		#rotation is a rotation unit quaternion
		self.rot = rotation * self.rot

	def changeScale(self,newScale):
		#newScale is a vec3
		self.scale = newScale

	def update(self):
		translate = makeTranslationMatrix(self.pos)
		rotate = makeQuatRotationMatrix(self.rot)
		scale = makeScaleMatrix(self.scale)
		self.model = translate * rotate * scale
	#the matrix to tranform the model into world space
	def modelMatrix(self):
		self.update()
		return self.model

# shape, has a color and contains triangles
class shape():
	def __init__(self, color, triangles):
		#triangles is a list of triangle objects
		self.triangles = triangles
		self.color = color

#contains 3 points
class triangle():
	def __init__(self, points):
		#points is a list of vec3s
		self.points = points
		v1 = points[0] - points[1]
		v2 = points[1] - points[2]
		self.normal = vec3CrossProduct(v1,v2)


#a light is a directional light in a scene
class light():
	def __init__(self,direction):
		#direction is a vec3
		self.direction = direction
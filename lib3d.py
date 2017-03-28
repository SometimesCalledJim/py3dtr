#by James Muir

import math
from math import sin
from math import cos
from math import tan

# a vector with three values
class vec3():
    def __init__(self,x=0,y=0,z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    #makes it iterable
    def __iter__(self):
        return iter((self.x,self.y,self.z))
    def __getitem__(self,index):
        return (self.x,self.y,self.z)[index]
    #length
    def norm(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    #math functions
    def __add__(a,b):
        if isinstance(b,vec3):
            x1,y1,z1 = a
            x2,y2,z2 = b
            return vec3(x1+x2,y1+y2,z1+z2)
        raise TypeError("Can't add vec3 and " + str(type(b)) + ".")
    def __sub__(a,b):
        if isinstance(b,vec3):
            x1,y1,z1 = a
            x2,y2,z2 = b
            return vec3(x1-x2,y1-y2,z1-z2)
        raise TypeError("Can't subtract " + str(type(b)) + " from vec3.")
    def __mul__(a,b):
        if isinstance(b, int) or isinstance(b, float):
            return vec3(a.x*b,a.y*b,a.z*b)
        raise TypeError("Can't multiply vec3 and " + str(type(b)) + ".")
    #so you can print it
    def __repr__(self):
        return "vec3(%f  %f  %f)" % (self.x,self.y,self.z)

#same as vector 3, but it has 4 values
#used for using matrices to translate points
class vec4():
    def __init__(self,x=0,y=0,z=0,w=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)
    def __iter__(self):
        return iter((self.x,self.y,self.z,self.w))
    def __getitem__(self,index):
        return (self.x,self.y,self.z,self.w)[index]
    def norm():
        return math.sqrt(self.x**2 + self.y**2 + self.z **2 + self.w**2)
    def __add__(a,b):
        if isinstance(b,vec4):
            x1,y1,z1,w1 = a
            x2,y2,z2,w2 = b
            return vec4(x1+x2,y1+y2,z1+z2,w1+w2)
        raise TypeError("Can't add vec4 and " + str(type(b)) + ".")
    def __sub__(a,b):
        if isinstance(b,vec4):
            x1,y1,z1,w1 = a
            x2,y2,z2,w2 = b
            return vec4(x1-x2,y1-y2,z1-z2,w1-w2)
        raise TypeError("Can't subtract " + str(type(b)) + " from vec4.")
    def __mul__(a,b):
        if isinstance(b, int) or isinstance(b, float):
            return vec3(a.x*b,a.y*b,a.z*b,a.w*b)
        raise TypeError("Can't multiply vec4 and " + str(type(b)) + ".")
    def __repr__(self):
        return "vec4(%f  %f  %f  %f)" % (self.x,self.y,self.z,self.w)

#quaternions, represent a rotation around an axis
class quat():
    def __init__(self,w=0,x=0,y=0,z=0):
        self.w = float(w)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    def __iter__(self):
        return iter((self.w,self.x,self.y,self.z))
    def __getitem__(self,index):
        return (self.w,self.x,self.y,self.z)[index]
    def norm(self):
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z **2)
    #multiplying quaternions yeilds a new quaternion
    #that represents the second quaternion's rotation
    #followed by the first quaternion's rotation
    def __mul__(a,b):
        if isinstance(b,quat):
            w1,x1,y1,z1 = a
            w2,x2,y2,z2 = b
            w3 = w1*w2 - x1*x2 - y1*y2 - z1*z2
            x3 = w1*x2 + x1*w2 + y1*z2 - z1*y2
            y3 = w1*y2 - x1*z2 + y1*w2 + z1*x2
            z3 = w1*z2 + x1*y2 - y1*x2 + z1*w2
            return quat(w3,x3,y3,z3)
        raise TypeError("Can't multiply quat by " + str(type(b)) + ".")
    def __repr__(self):
            return "quat(%f  %f  %f  %f)" % (self.w,self.x,self.y,self.z)

#a 4 by 4 matrix
class mat4():
    # m row col
    def __init__(self, 
                m00=0,m01=0,m02=0,m03=0,
                m10=0,m11=0,m12=0,m13=0,
                m20=0,m21=0,m22=0,m23=0,
                m30=0,m31=0,m32=0,m33=0):
        #row 0
        self.m00 = float(m00)
        self.m01 = float(m01)
        self.m02 = float(m02)
        self.m03 = float(m03)
        #row 1
        self.m10 = float(m10)
        self.m11 = float(m11)
        self.m12 = float(m12)
        self.m13 = float(m13)
        #row 2
        self.m20 = float(m20)
        self.m21 = float(m21)
        self.m22 = float(m22)
        self.m23 = float(m23)
        #row 3
        self.m30 = float(m30)
        self.m31 = float(m31)
        self.m32 = float(m32)
        self.m33 = float(m33)

        #so i can deal with both row and column major storage paradigms

        #rows:
        self.row0 = (self.m00,self.m01,self.m02,self.m03)
        self.row1 = (self.m10,self.m11,self.m12,self.m13)
        self.row2 = (self.m20,self.m21,self.m22,self.m23)
        self.row3 = (self.m30,self.m31,self.m32,self.m33)
        #cols:
        self.col0 = (self.m00,self.m10,self.m20,self.m30)
        self.col1 = (self.m01,self.m11,self.m21,self.m31)
        self.col2 = (self.m02,self.m12,self.m22,self.m32)
        self.col3 = (self.m03,self.m13,self.m23,self.m33)

    #math functions
    def __mul__(a,b):
        if isinstance(b,mat4):
            #needs to be long because it's a matrix
            return mat4(
                    dotProduct(a.row0,b.col0), dotProduct(a.row0,b.col1), dotProduct(a.row0,b.col2), dotProduct(a.row0,b.col3),
                    dotProduct(a.row1,b.col0), dotProduct(a.row1,b.col1), dotProduct(a.row1,b.col2), dotProduct(a.row1,b.col3),
                    dotProduct(a.row2,b.col0), dotProduct(a.row2,b.col1), dotProduct(a.row2,b.col2), dotProduct(a.row2,b.col3),
                    dotProduct(a.row3,b.col0), dotProduct(a.row3,b.col1), dotProduct(a.row3,b.col2), dotProduct(a.row3,b.col3)
                    )
        if isinstance(b,vec4):
            return vec4(
                dotProduct(a.row0,b),
                dotProduct(a.row1,b),
                dotProduct(a.row2,b)
                )
        if isinstance(b,float) or isinstance(b,int):
            return mat4(a.m00*b, a.m01*b, a.m02*b, a.m03*b,
                a.m10*b, a.m11*b, a.m12*b, a.m13*b,
                a.m20*b, a.m21*b, a.m22*b, a.m23*b,
                a.m30*b, a.m31*b, a.m32*b, a.m33*b
                )
        raise TypeError("Can't multiply mat4 by " + str(type(b)) + ".")
    
    def __add__(a,b):
        if isinstance(b,mat4):
            return mat4(a.m00+b.m00, a.m01+b.m01, a.m02+b.m02, a.m03+b.m03,
                a.m10+b.m10, a.m11+b.m11, a.m12+b.m12, a.m13+b.m13,
                a.m20+b.m20, a.m21+b.m21, a.m22+b.m22, a.m23+b.m23,
                a.m30+b.m30, a.m31+b.m31, a.m32+b.m32, a.m33+b.m33
                )
        raise TypeError("Can't add mat4 and " + str(type(b)) + ".")
    
    def __sub__(a,b):
        if isinstance(b,mat4):
            return mat4(a.m00-b.m00, a.m01-b.m01, a.m02-b.m02, a.m03-b.m03,
                a.m10-b.m10, a.m11-b.m11, a.m12-b.m12, a.m13-b.m13,
                a.m20-b.m20, a.m21-b.m21, a.m22-b.m22, a.m23-b.m23,
                a.m30-b.m30, a.m31-b.m31, a.m32-b.m32, a.m33-b.m33
                )
        raise TypeError("Can't subtract " + str(type(b)) + " from mat4.")
    #so you can print things
    def __repr__(self):
        return """mat4(%f  %f  %f  %f
    %f  %f  %f  %f
    %f  %f  %f  %f
    %f  %f  %f  %f)""" % (self.m00,self.m01,self.m02,self.m03,
                self.m10,self.m11,self.m12,self.m13,
                self.m20,self.m21,self.m22,self.m23,
                self.m30,self.m31,self.m32,self.m33)

#unit vectors

unitvx = vec3(1,0,0)

unitvy = vec3(0,1,0)

unitvz = vec3(0,0,1)


#makes a matrix that translates points
def makeTranslationMatrix(vector3):
    return mat4(
        1,0,0,vector3.x,
        0,1,0,vector3.y,
        0,0,1,vector3.z,
        0,0,0,1
        )

#returns an identity matrix
def identityMat4():
    return mat4(
        1,0,0,0,
        0,1,0,0,
        0,0,1,0,
        0,0,0,1
        )

#flips matrix on the top left to bottom right diagonal
def transposeMat4(matrix):
    return mat4(
        matrix.m00,matrix.m10,matrix.m20,matrix.m30,
        matrix.m01,matrix.m11,matrix.m21,matrix.m31,
        matrix.m02,matrix.m12,matrix.m22,matrix.m32,
        matrix.m03,matrix.m13,matrix.m23,matrix.m33
        )

#gives orthagonal vector
def vec3CrossProduct(vector1, vector2):
    #vector one and vector two are tuples
    #returns a vector
    x1,y1,z1 = vector1
    x2,y2,z2 = vector2
    return vec3(y1*z2-z1*y2, z1*x2-x1*z2, x1*y2-y2*x2)

#finds the angle between two vectors
def findAngle(vector1, vector2):
    if vector1.norm()*vector2.norm() == 0:
        return math.pi
    ivector1 = vector1
    ivector2 = vector2
    return math.acos(dotProduct(ivector1,\
        ivector2)/vector1.norm()*vector2.norm())

#return norm (magnitude) of a vector
def norm(vector):
    x,y,z = vector
    return math.sqrt(x**2+y**2+z**2)
 
#dot product of iterables 
def dotProduct(a, b):
    ans = 0
    for i in range(len(a)):
        ans += a[i]*b[i]
    return ans

#makes a rotation matrix given a quaternion
def makeQuatRotationMatrix(quat):
    w,x,y,z = quat
    a = mat4(
        w,z,-y,x,
        -z,w,x,y,
        y,-x,w,z,
        -x,-y,-z,w)
    b = mat4(
        w,z,-y,-x,
        -z,w,x,-y,
        y,-x,w,-z,
        x,y,z,w)
    return a * b

#makes a quaternion representing a rotation by 
#an angle around a unit vector
def makeRotationQuat(angle, unitv):
    xv,yv,zv = unitv
    semia = angle/2
    wq = cos(semia)
    xq = xv * sin(semia)
    yq = yv * sin(semia)
    zq = zv * sin(semia)
    return quat(wq,xq,yq,zq)

#makes a scaling matrix
def makeScaleMatrix(vector3):
    return mat4(
        vector3.x,0,0,0,
        0,vector3.y,0,0,
        0,0,vector3.z,0,
        0,0,0,1
        )

#converts from coords in vec4 after tranformation by perpective matrix
#back to vec3 coords in normal 3D x,y,z space
def homogenousToNormalCoords(homogenousCoords):
    return vec3(homogenousCoords.x/homogenousCoords.w,
        homogenousCoords.y/homogenousCoords.w,
        homogenousCoords.z/homogenousCoords.w)

#makes a projection matrix, which takes homogenous coordinates
#and puts them in screen space
def makeProjectionMatrix(fov,aspectRatio,nearClip,farClip):
    #fov is the vertical field of view
    #nearClip and farClip must be positive
    f = 1/tan(fov/2)
    return mat4(
        f/aspectRatio, 0, 0, 0,
        0, f, 0, 0,
        0, 0, (nearClip+farClip)/(nearClip-farClip),\
         2*nearClip*farClip/(nearClip-farClip),
        0, 0, -1, 0
        )

#check if a quaternion needs to be normalized
def quatNeedsNormalizing(quat, tolerance):
    w,x,y,z = quat
    if (1-tolerance)<(w**2 + x**2 + y**2 + z**2)<(1+tolerance):
        return True
    else:
        return False

#normalizes a quaterion
def normalizeQuat(quat):
    w,x,y,z = quat
    magnitude = quat.norm()
    w /= magnitude
    x /= magnitude
    y /= magnitude
    z /= magnitude
    return (w,x,y,z)

# #how to use library to transform a point
# rotQuat1 = makeRotationQuat(math.pi/2, vec3(0,0,1))
# print(rotQuat1)
# rotQuat2 = makeRotationQuat(math.pi/2, vec3(1,0,0))
# print(rotQuat2)
# rotQuat3 = makeRotationQuat(-math.pi/2, vec3(0,1,0))
# print(rotQuat3)
# scale = makeScalingMatrix(2,0,0)
# trans = makeTranslationMatrix(1,0,0)
# proj = makeProjectionMatrix(math.pi/2,8/6,1,100)
# #1 first, then 2, then 3 are applied
# rotQuat = rotQuat3 * rotQuat2 * rotQuat1
# print(rotQuat)
# rot = makeQuatRotationMatrix(rotQuat)
# point = vec4(1,0,0,1)
# print(point)
# #note: scale is applied first, then rot, then trans
# newPoint = proj * trans * rot * scale * point
# print(newPoint)

#some tests to see which order things are applied in
# a = vec4(1,1,2,3)
# b = makeTranslationMatrix(5,5,5)
# c = makeScalingMatrix(2,2,2)
# d = b * c
# e = d * a
# print(e)

#multiplication test
# a = quat(1,3,4,2)
# b = quat(1,0,0,0)
# print(b*a)

#vector subtraction
# print(vec3(1,2,3)-vec3(2,3,1))
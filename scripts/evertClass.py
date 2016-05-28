from bge import logic as gl
import bgl
# print (__name__)
# import scripts.evertMethods as evertMethods

class Path():

	def __init__(self, ID):
		# if gl.dbg: print ('Path Created')
		self.linesDict = {}
		self.length = 0
		self.ID = ID

	def setLine(self, ID, p1, p2, absorption):
		self.linesDict[ID] = Line(ID,p1,p2,absorption)

		# if gl.dbg: print ('setPoint', ID, coordinates, absorption)


	def printLines(self):
		# print('- lines in Path', self.ID)
		print ('-> recorded pathID', self.ID)
		for lineID in self.linesDict.keys():
			# (pathID, order, (coord0), (coordN), dist, (abs))
			print (' \t order: ', self.linesDict[lineID].ID, '\n \t length ', self.length, '\n \t coord1    ', self.linesDict[lineID].p1, '\n \t coordN ('+str(lineID)+')', self.linesDict[lineID].p2, '\n  \t absorption', self.linesDict[lineID].abs)
		print ('')

class Point():

	def __init__(self, coordinates, absorption):
		# if gl.dbg: print ('Point Created')
		self.coordinates = coordinates
		self.absorption = absorption

	def getCoordinates(self):
		return self.coordinates

	def getAbsorption(self):
		return self.absorption


class Line():

	def __init__(self, ID, p1, p2, absorption = (0,0,0,0,0,0,0,0)):
		# if gl.dbg: print ('Path Created')
		self.ID = ID
		self.posInPost_draw = 0
		self.p1 = p1
		self.p2 = p2
		self.abs = absorption

	def setAbs(self, absorption):
		self.abs = absorption

	def setCoord(self, p1, p2):
		self.p1 = p1
		self.p2 = p2
		# if gl.dbg:  print ('Set Coords line', self.ID, ':', self.p1, self.p2)

	def drawPath(self):
		vectOrigin = self.p1
		vectDest = self.p2
		width = 1
		bgl.glColor4f(0.4,0.4,0.4,0.3)
		bgl.glLineWidth(width)
		bgl.glBegin(bgl.GL_LINES)

		# try:
		# if self.p2
		bgl.glVertex3f(vectOrigin[0],vectOrigin[1],vectOrigin[2])
		bgl.glVertex3f(vectDest[0],vectDest[1],vectDest[2])
		bgl.glEnd()

		# except IndexError:
			# print ('..')

			# gl.rayMissed += 1
			# if gl.dbg and gl.rayMissed > 10:
			# 	print ('\n')
		bgl.glNormal3f(0.0,0.0,1.0)
		bgl.glShadeModel(bgl.GL_SMOOTH);

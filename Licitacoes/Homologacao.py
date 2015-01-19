#!/usr/bin/python
#coding: utf-8
from DiarioTools.Parser import *
from DiarioTools.Process import *
from DiarioTools.Search import *
from DiarioTools.Log import *
import re
import locale

class ParseHomologacao(GenericParser):
	def Initialize(self):
		self.AddExpression("(\(\(TITULO\)\)|^)HOMOLOGA..O", [0], re.I|re.M, 1)
		self.AddExpression("\d{4}-\d.\d{3}.\d{3}(-\d)?", [0], re.M, 1)
		self.AddExpression("Preg.o (Eletr.nico|Presencial)[^\d]{,50}([^,\s]*)", [1,2],re.I|re.M, 1)
		self.AddExpression("total de R\$\.?\s*([\d,.]*)", [1],re.I|re.M)		

class SearchHomologacao(DlSearch):
	def SetOptions(self):		
		self.options["f[tipo_conteudo_facet][]"] = "LICITAÇÕES"
		self.options["sort"] = u"data desc"
		self.query = "HOMOLOGAÇÂO"

class ProcessorHomologacao(ResponseProcessor):
	def __init__(self, configInstance, searchObject, parseObject, fileName, sessionName):
		super(ProcessorHomologacao, self).__init__(configInstance, searchObject, parseObject, sessionName)
		self.fileName = fileName
		self.records = []
		self.expressions = []
		self.itemClass = 0

		with open(self.fileName, "a") as fd:
			 fd.write("*** Homologações ***\r\n")
	def Persist(self, data):
	    if len(data) > 0 and re.search("HOMOLOGA..O", data[0], re.I) is not None:
		self.expressions = []
		self.expressions.append(data)
	    elif len(self.expressions) > 0:
		self.expressions.append(data)

	def Iterate(self):	    
	    if len(self.expressions) > 0:
		strOut = """Em """ + self.GetDateFromId() + """,""" + self.GetSecretaty() + """ homologou o pregão """.decode("utf-8") + self.GetEvent() + """, processo """ + self.GetProcess() + self.GetTotals() + ".\r\n"
		self.records.append(strOut)
		with open(self.fileName, "a") as fd:
			 fd.write(strOut.encode("utf-8"))
		self.expressions = []

	def ProcessEnd(self):			
		message = "*** Homologações ***\r\n".decode("utf-8")
		if (len(self.records) == 0):    
		    message += """Pregão foi homologado no período\r\n\r\n""".decode("utf-8")
		    Log.Log("Sem Alterações")
		else:
		    message += "\r\n".join(self.records)
		return message

	def GetEvent(self):
	    if len(self.expressions[2]) < 2:
		return "-"
	    return self.expressions[2][0] + " " + self.expressions[2][1]

	def GetProcess(self):
	    if len(self.expressions[1]) < 1:
		return "-"
	    return self.expressions[1][0]
		
	def GetTotals(self):
	    sum = 0
	    retStr = ""
	    for i in self.expressions[3:]:
		if len(i) > 0 is not None:
		    value = i[0]
		    value = re.sub("\.", "", value)
		    value = re.sub(",", ".", value)
		    value = re.sub("\.$", "", value)		    
		    try:
			sum += float(value)
		    except:
			Log.Warning("Could not convert value")
	    if sum > 0:
		locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
		numVal = locale.format("%.2f", sum, True)
		retStr = " ,no valor total de R$ " + numVal
	    return retStr

		

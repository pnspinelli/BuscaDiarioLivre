#!/usr/bin/python
#coding: utf-8
from Licitacoes.Homologacao import *
from DiarioTools.Config import Configuration
from DiarioTools.GMailer import *
from DiarioTools.Log import *
import datetime
import sys

def HandleHomologacao(configInstance):
    searcher = SearchHomologacao(configInstance, True)
    parser = ParseHomologacao()
    processor = ProcessorHomologacao(configInstance, searcher, parser, configInstance.logName, "Homologacao")
    return processor.Process()

try:
    config = Configuration("config_licitacoes.xml", sys.argv) 
    Log.Log("Searching Homologacoes")
    messages = HandleHomologacao(config)

    if (config.mode == "alert mode"):
	messages = "Relatório de ".decode("utf-8") + datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S") + "\r\n\r\n" + messages
	messages = messages.encode("utf-8")
	Log.Log("Enviando E-Mail")
	mailer = GMailerWrappper(config)    
	mailer.Send(messages)
except Exception as e:
    Log.Warning("Problemas encontrados durante a execução do script")
    Log.Warning(str(e))



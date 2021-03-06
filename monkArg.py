#!/usr/bin/python
import sys
import monkDebug as debug

class ArgElement:
	def __init__(self, option, value=""):
		self.option = option;
		self.arg = value;
	
	def get_option_name(self):
		return self.option
	
	def get_arg(self):
		return self.arg
	
	def display(self):
		if len(self.arg)==0:
			debug.info("option : " + self.option)
		elif len(self.option)==0:
			debug.info("element :       " + self.arg)
		else:
			debug.info("option : " + self.option + ":" + self.arg)


class ArgDefine:
	def __init__(self,
	             smallOption="", # like v for -v
	             bigOption="", # like verbose for --verbose
	             list=[], # ["val", "description"]
	             desc="",
	             haveParam=False):
		self.option_small = smallOption;
		self.option_big = bigOption;
		self.list = list;
		if len(self.list)!=0:
			self.have_param = True
		else:
			if True==haveParam:
				self.have_param = True
			else:
				self.have_param = False
		self.description = desc;
	
	def get_option_small(self):
		return self.option_small
		
	def get_option_big(self):
		return self.option_big
	
	def need_parameters(self):
		return self.have_param
	
	def get_porperties(self):
		return ""
	
	def check_availlable(self, argument):
		if len(self.list)==0:
			return True
		for element,desc in self.list:
			if element == argument:
				return True
		return False
	
	def display(self):
		if self.option_small != "" and self.option_big != "":
			print("		-" + self.option_small + " / --" + self.option_big)
		elif self.option_small != "":
			print("		-" + self.option_small)
		elif self.option_small != "":
			print("		--" + self.option_big)
		else:
			print("		???? ==> internal error ...")
		if self.description != "":
			print("			" + self.description)
		if len(self.list)!=0:
			hasDescriptiveElement=False
			for val,desc in self.list:
				if desc!="":
					hasDescriptiveElement=True
					break;
			if hasDescriptiveElement==True:
				for val,desc in self.list:
					print("				" + val + " : " + desc)
			else:
				tmpElementPrint = ""
				for val,desc in self.list:
					if len(tmpElementPrint)!=0:
						tmpElementPrint += " / "
					tmpElementPrint += val
				print("				{ " + tmpElementPrint + " }")
	
	def parse(self, argList, currentID):
		return currentID;


class ArgSection:
	def __init__(self,
	             sectionName="",
	             desc=""):
		self.section = sectionName;
		self.description = desc;
	
	def get_option_small(self):
		return ""
		
	def get_option_big(self):
		return ""
		
	def get_porperties(self):
		return " [" + self.section + "]"
	
	def display(self):
		print("	[" + self.section + "] : " + self.description)
	
	def parse(self, argList, currentID):
		return currentID;


class MonkArg:
	def __init__(self):
		self.list_properties = []
	
	def add(self, argument):
		self.list_properties.append(argument) #argDefine(smallOption, bigOption, haveParameter, parameterList, description));
	
	def add_section(self, sectionName, sectionDesc):
		self.list_properties.append(ArgSection(sectionName, sectionDesc))
	
	def parse(self):
		listArgument = [] # composed of list element
		NotParseNextElement=False
		for iii in range(1, len(sys.argv)):
			# special case of parameter in some elements
			if NotParseNextElement==True:
				NotParseNextElement = False
				continue
			debug.verbose("parse [" + str(iii) + "]=" + sys.argv[iii])
			argument = sys.argv[iii]
			optionList = argument.split("=")
			debug.verbose(str(optionList))
			if type(optionList) == type(str()):
				option = optionList
			else:
				option = optionList[0]
			optionParam = argument[len(option)+1:]
			debug.verbose(option)
			argumentFound=False;
			if option[:2]=="--":
				# big argument
				for prop in self.list_properties:
					if prop.get_option_big()=="":
						continue
					if prop.get_option_big() == option[2:]:
						# find it
						debug.verbose("find argument 2 : " + option[2:])
						if prop.need_parameters()==True:
							internalSub = option[2+len(prop.get_option_big()):]
							if len(internalSub)!=0:
								if len(optionParam)!=0:
									# wrong argument ...
									debug.warning("maybe wrong argument for : '" + prop.get_option_big() + "' cmdLine='" + argument + "'")
									prop.display()
									continue
								optionParam = internalSub
							if len(optionParam)==0:
								#Get the next parameters 
								if len(sys.argv) > iii+1:
									optionParam = sys.argv[iii+1]
									NotParseNextElement=True
								else :
									# missing arguments
									debug.warning("parsing argument error : '" + prop.get_option_big() + "' Missing : subParameters ... cmdLine='" + argument + "'")
									prop.display()
									exit(-1)
							if prop.check_availlable(optionParam)==False:
								debug.warning("argument error : '" + prop.get_option_big() + "' SubParameters not availlable ... cmdLine='" + argument + "' option='" + optionParam + "'")
								prop.display()
								exit(-1)
							listArgument.append(ArgElement(prop.get_option_big(),optionParam))
							argumentFound = True
						else:
							if len(optionParam)!=0:
								debug.warning("parsing argument error : '" + prop.get_option_big() + "' need no subParameters : '" + optionParam + "'   cmdLine='" + argument + "'")
								prop.Display()
							listArgument.append(ArgElement(prop.get_option_big()))
							argumentFound = True
						break;
				if False==argumentFound:
					debug.error("UNKNOW argument : '" + argument + "'")
			elif option[:1]=="-":
				# small argument
				for prop in self.list_properties:
					if prop.get_option_small()=="":
						continue
					if prop.get_option_small() == option[1:1+len(prop.get_option_small())]:
						# find it
						debug.verbose("find argument 1 : " + option[1:1+len(prop.get_option_small())])
						if prop.need_parameters()==True:
							internalSub = option[1+len(prop.get_option_small()):]
							if len(internalSub)!=0:
								if len(optionParam)!=0:
									# wrong argument ...
									debug.warning("maybe wrong argument for : '" + prop.get_option_big() + "' cmdLine='" + argument + "'")
									prop.display()
									continue
								optionParam = internalSub
							if len(optionParam)==0:
								#Get the next parameters 
								if len(sys.argv) > iii+1:
									optionParam = sys.argv[iii+1]
									NotParseNextElement=True
								else :
									# missing arguments
									debug.warning("parsing argument error : '" + prop.get_option_big() + "' Missing : subParameters  cmdLine='" + argument + "'")
									prop.display()
									exit(-1)
							if prop.check_availlable(optionParam)==False:
								debug.warning("argument error : '" + prop.get_option_big() + "' SubParameters not availlable ... cmdLine='" + argument + "' option='" + optionParam + "'")
								prop.display()
								exit(-1)
							listArgument.append(ArgElement(prop.get_option_big(),optionParam))
							argumentFound = True
						else:
							if len(optionParam)!=0:
								debug.warning("parsing argument error : '" + prop.get_option_big() + "' need no subParameters : '" + optionParam + "'  cmdLine='" + argument + "'")
								prop.display()
							listArgument.append(ArgElement(prop.get_option_big()))
							argumentFound = True
						break;
			
			if argumentFound==False:
				#unknow element ... ==> just add in the list ...
				debug.verbose("unknow argument : " + argument)
				listArgument.append(ArgElement("", argument))
			
		#for argument in listArgument:
		#	argument.Display()
		#exit(0)
		return listArgument;
	
	
	
	def display(self):
		print("usage:")
		listOfPropertiesArg = "";
		for element in self.list_properties :
			listOfPropertiesArg += element.get_porperties()
		print("	" + sys.argv[0] + listOfPropertiesArg + " ...")
		for element in self.m_list_properties :
			element.display()

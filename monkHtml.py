#!/usr/bin/python
import monkDebug as debug
import sys
import monkTools as tools
#import CppHeaderParser
import os
import re
import codeBB
import codeMarkDown
import collections
import monkModule as module
import monkNode as node

htmlCodes = (
	('&', '&amp;'),
	("'", '&#39;'),
	('"', '&quot;'),
	('>', '&gt;'),
	('<', '&lt;')
)
def html_decode(s):
	for code in htmlCodes:
		s = s.replace(code[1], code[0])
	return s
def html_encode(s):
	for code in htmlCodes:
		s = s.replace(code[0], code[1])
	return s

camelCaseCodes = (
	('A', ' a'),
	('B', ' b'),
	('C', ' c'),
	('D', ' d'),
	('E', ' e'),
	('F', ' f'),
	('G', ' g'),
	('H', ' h'),
	('I', ' i'),
	('J', ' j'),
	('K', ' k'),
	('L', ' l'),
	('M', ' m'),
	('N', ' n'),
	('O', ' o'),
	('P', ' p'),
	('Q', ' q'),
	('R', ' r'),
	('S', ' s'),
	('T', ' t'),
	('U', ' u'),
	('V', ' v'),
	('W', ' w'),
	('X', ' x'),
	('Y', ' y'),
	('Z', ' z'),
)
def camel_case_encode(s):
	for code in camelCaseCodes:
		s = s.replace(code[1], code[0])
	return s
def camel_case_decode(s):
	for code in camelCaseCodes:
		s = s.replace(code[0], code[1])
	while s[0] == ' ':
		s = s[1:]
	return s

def capitalise_first_letter(s):
	s2 = " " + s[0]
	ret = camel_case_encode(s2) + s[1:]
	debug.info("'" + s + "' => '" + ret + "'")
	return ret;

def display_doxygen_param(comment, input, output):
	data = '<tr>'
	data = '<td>'
	data += "<b>Parameter"
	if input == True:
		data += " [input]"
	if output == True:
		data += " [output]"
	data += ":</b>"
	data += '</td>'
	#extract first element:
	val = comment.find(" ")
	var = comment[:val]
	endComment = comment[val:]
	data += '<td>'
	# TODO : Check if it exist in the parameter list ...
	data += "<span class=\"code-argument\">" + var + "</span> "
	data += '</td>'
	data += '<td>'
	data += codeBB.transcode(endComment)
	data += '</td>'
	data += '</tr>\n'
	return data


def parse_doxygen(data) :
	data = "\n" + data
	if '@' in data:
		streams = data.split("\n@")
	else:
		streams = [ "brief " + data]
	data2 = ''
	for element in streams:
		if    element[:1] == "\n" \
		   or element[:2] == "\n\n":
			# nothing to do : Nomale case of the first \n
			None
		elif element[:6] == "brief ":
			data2 += codeBB.transcode(element[6:])
			data2 += '<br/>'
	
	for element in streams:
		if    element[:1] == "\n" \
		   or element[:2] == "\n\n":
			# nothing to do : Nomale case of the first \n
			None
		elif element[:5] == "note ":
			data2 += '<b>Note:</b> '
			data2 += codeBB.transcode(element[5:])
			data2 += '<br/> '
	
	data3 = ''
	dataReturn = ''
	for element in streams:
		if    element[:1] == "\n" \
		   or element[:2] == "\n\n":
			# nothing to do : Nomale case of the first \n
			pass
		elif    element[:14] == "param[in,out] " \
		     or element[:14] == "param[out,in] ":
			data3 += display_doxygen_param(element[14:], True, True)
		elif element[:10] == "param[in] ":
			data3 += display_doxygen_param(element[10:], True, False)
		elif element[:11] == "param[out] ":
			data3 += display_doxygen_param(element[11:], False, True)
		elif element[:6] == "param ":
			data3 += display_doxygen_param(element[6:], False, False)
		elif element[:7] == "return ":
			if dataReturn != "":
				dataReturn += '<br/>'
			dataReturn += element[7:]
	if    data3 != '' \
	   or dataReturn != '':
		data2 += '<ul>\n'
		data2 += '<table class="parameter-list">\n'
		data2 += data3
		if dataReturn != "":
			data2 += '<tr><td>'
			data2 += '<b>Return: </b>'
			data2 += '</td><td></td><td>'
			data2 += codeBB.transcode(dataReturn)
			data2 += '</td></tr>'
		data2 += '</table>\n'
		data2 += '</ul>\n'
	return data2

def white_space(size) :
	ret = ''
	for iii in range(len(ret), size):
		ret += " "
	return ret

def generate_menu(element, level=1):
	namespaceStack = element.get_namespace()
	listBase = element.get_all_sub_type(['namespace'])
	if len(listBase) == 0:
		return ""
	ret = ""
	ret += '<ul class="niveau' + str(level) + '">\n'
	for element in listBase:
		retTmp = generate_menu(element['node'], level+1)
		if retTmp != "":
			subMenu = ' class="sousmenu"'
		else:
			subMenu = ''
		ret += '	<li' + subMenu + '>' + generate_link(element['node']) + '\n'
		ret += retTmp
		ret += '	</li>\n'
	ret += '</ul>\n'
	return ret

def generate_html_page_name(element):
	return element.get_doc_website_page_local()

def generate_name(element):
	namespaceStack = element.get_namespace()
	namespaceExpanded = ""
	for name in namespaceStack:
		namespaceExpanded += name + "::"
	if element.get_name() == "":
		return element.get_node_type()
	return element.get_node_type() + ": " + namespaceExpanded + element.get_name()

def generate_link(element):
	if element.get_name() == "":
		return '<a href="' + generate_html_page_name(element) + '">** No name **</a>'
	return '<a href="' + generate_html_page_name(element) + '">' + element.get_name() + '</a>'

def calculate_methode_size(list):
	returnSize = 0;
	methodeSize = 0;
	haveVirtual = False
	for element in list:
		debug.info("node type = " + element['node'].get_node_type())
		if     element['node'].get_node_type() == 'methode' \
		    or element['node'].get_node_type() == 'constructor' \
		    or element['node'].get_node_type() == 'destructor':
			if element['node'].get_virtual() == True:
				haveVirtual = True
		if element['node'].get_node_type() == 'variable':
			retType = element['node'].get_type().to_str()
		elif element['node'].get_node_type() == 'using':
			retType = ""
		else:
			retType = element['node'].get_return_type().to_str()
		tmpLen = len(retType)
		if returnSize < tmpLen:
			returnSize = tmpLen
		tmpLen = len(element['node'].get_name())
		if methodeSize < tmpLen:
			methodeSize = tmpLen
	return [returnSize, methodeSize, haveVirtual]


def write_methode(element, namespaceStack, displaySize = None, link = True):
	if element['node'].get_request_hidden() == True:
		return ""
	if displaySize == None:
		displaySize = calculate_methode_size([element])
	ret = ""
	if 'access' in element.keys():
		if element['access'] == 'private':
			ret += '- '
			return ""
		elif element['access'] == 'protected':
			ret += '# '
		elif element['access'] == 'public':
			ret += '+ '
		else:
			ret += '  '
	else:
		ret += '  '
	
	if element['node'].get_node_type() in ['variable']:
		if displaySize[2] == True:
			ret += '        '
		raw, decorated = element['node'].get_type().to_str_decorated()
	elif element['node'].get_node_type() in ['using']:
		if displaySize[2] == True:
			ret += '        '
		raw, decorated = element['node'].get_type().to_str_decorated()
	else:
		if element['node'].get_virtual() == True:
			ret += module.display_color('virtual') + ' '
		elif displaySize[2] == True:
			ret += '        '
		
		raw, decorated = element['node'].get_return_type().to_str_decorated()
	if raw != "":
		ret += decorated
		ret += " "
		raw += " "
	
	ret += white_space(displaySize[0] - len(raw)+1)
	name = element['node'].get_name()
	
	if element['node'].get_node_type() == 'variable':
		classDecoration = "code-member"
	else:
		classDecoration = "code-function"
	
	if link == True:
		ret += '<a class="' + classDecoration + '" href="#' + str(element['node'].get_uid()) + '">' + name + '</a>'
	else:
		ret += '<span class="' + classDecoration + '">' + name + '</span>'
	
	if element['node'].get_node_type() not in ['variable', 'using']:
		ret += white_space(displaySize[1] - len(name)) + ' ('
		listParam = element['node'].get_param()
		first = True
		for param in listParam:
			if first == False:
				ret += ',<br/>'
				if displaySize[2] == True:
					ret += '        '
				ret += white_space(displaySize[0] + displaySize[1] +5)
			first = False
			typeNoDecoration, typeDecorated = param.get_type().to_str_decorated()
			#retParam = module.display_color(param.get_type().to_str())
			retParam = typeDecorated
			if retParam != "":
				ret += retParam
				ret += " "
			ret += "<span class=\"code-argument\">" + param.get_name() + "</span>"
		ret += ')'
		if element['node'].get_constant() == True:
			ret += module.display_color(' const')
		if element['node'].get_override() == True:
			ret += module.display_color(' override')
		if element['node'].get_virtual_pure() == True:
			ret += ' = 0'
		if element['node'].get_delete() == True:
			ret += ' = delete'
	
	ret += ';'
	ret += '<br/>'
	return ret

def generate_stupid_index_page(outFolder, header, footer, my_lutin_doc):
	# create index.hml : 
	filename = outFolder + "/index.html"
	tools.create_directory_of_file(filename);
	file = open(filename, "w")
	file.write(header)
	file.write("<h1>" + my_lutin_doc.get_base_doc_node().get_name() + "</h1>");
	file.write("<br/>");
	file.write("TODO : Main page ...");
	file.write("<br/>");
	file.write("<br/>");
	file.write(footer)
	file.close();

def generate_page(outFolder, header, footer, element, name_lib=""):
	debug.print_element("code-doc", name_lib, "<==", element.name)
	currentPageSite = element.get_doc_website_page()
	namespaceStack = element.get_namespace()
	if element.get_node_type() in ['library', 'application', 'namespace', 'class', 'struct', 'enum', 'union', 'using']:
		listBase = element.get_all_sub_type(['library', 'application', 'namespace', 'class', 'struct', 'enum', 'union', 'using'])
		for elem in listBase:
			generate_page(outFolder, header, footer, elem['node'], name_lib)
	filename = outFolder + '/' + generate_html_page_name(element)
	tools.create_directory_of_file(filename);
	file = open(filename, "w")
	file.write(header)
	file.write('<h1>' + generate_name(element) + '</h1>');
	file.write('<hr/>');
	
	documentation = parse_doxygen(element.get_doc())
	if len(documentation) != 0:
		file.write('<h2>Description:</h2>\n')
		file.write(documentation)
		file.write('<br/>\n')
	
	if element.get_node_type() in ['namespace']:
		tmpName = element.get_name()
		tmpNameUpper = tmpName.upper()
		tmpName = tmpNameUpper[0] + tmpName[1:]
		compleateName = ""
		for namespace in element.get_namespace():
			compleateName += namespace + "::"
		compleateName += tmpName
		associatedClass = module.get_element_with_name(compleateName)
		if associatedClass != None:
			file.write('<h2>Associated Class:</h2>');
			file.write('<ul>\n');
			file.write(generate_link(associatedClass));
			file.write('</ul>\n');
	
	if element.get_node_type() in ['class']:
		tmpName = element.get_name()
		tmpNameLower = tmpName.lower()
		tmpName = tmpNameLower[0] + tmpName[1:]
		compleateName = ""
		for namespace in element.get_namespace():
			compleateName += namespace + "::"
		compleateName += tmpName
		associatedClass = module.get_element_with_name(compleateName)
		if associatedClass != None:
			file.write('<h2>Associated Namespace:</h2>');
			file.write('<ul>\n');
			file.write(generate_link(associatedClass));
			file.write('</ul>\n');
	
	if element.get_node_type() in ['library', 'application', 'namespace', 'class', 'struct']:
		for nameElement in ['namespace', 'class', 'struct', 'enum', 'union', 'using']:
			listBase = element.get_all_sub_type(nameElement)
			if len(listBase) == 0:
				continue
			descLocal = ""
			for elem in listBase:
				if elem['node'].get_request_hidden() == True:
					continue
				if     'access' in elem.keys() \
				   and elem['access'] == 'private':
					continue
				descLocal += '<li>' + generate_link(elem['node']) + '</li>'
			if descLocal != "":
				file.write('<h2>' + nameElement + ':</h2>\n');
				file.write('<ul>\n');
				file.write(descLocal)
				file.write('</ul>\n');
		
	# calculate element size :
	listBase = element.get_all_sub_type(['methode', 'constructor', 'destructor', 'variable', 'using'])
	displayLen = calculate_methode_size(listBase)
	
	if    element.get_node_type() == 'class' \
	   or element.get_node_type() == 'struct':
		if len(element.get_all_sub_type(['constructor', 'destructor'])) != 0:
			globalWrite = ""
			listBaseConstructor = element.get_all_sub_type(['constructor'])
			for elem in listBaseConstructor:
				if elem['access'] == 'private':
					continue
				globalWrite += write_methode(elem, namespaceStack, displayLen)
			listBaseDestructor = element.get_all_sub_type(['destructor'])
			for elem in listBaseDestructor:
				if elem['access'] == 'private':
					continue
				globalWrite += write_methode(elem, namespaceStack, displayLen)
			if globalWrite != "":
				file.write('<h2>Constructor and Destructor:</h2>\n')
				file.write('<pre>\n');
				file.write(globalWrite);
				file.write('</pre>\n');
				file.write('<br/>\n')
	
	if element.get_node_type() in ['library', 'application', 'namespace', 'class', 'struct']:
		listBaseMethode = element.get_all_sub_type(['methode', 'variable', 'using'])
		if len(listBaseMethode) != 0:
			globalWrite = ""
			globalWriteProperties = ""
			globalWriteSignals = ""
			displayLen = calculate_methode_size(listBaseMethode)
			for elem in listBaseMethode:
				if     'access' in elem.keys() \
				   and elem['access'] == 'private':
					continue
				find_special = False
				if     'node' in elem.keys() \
				   and elem['node'].get_node_type() == 'variable':
					name = elem['node'].get_name()
					if     len(name) > 8 \
					   and name[:8] == "property":
						globalWriteProperties += write_methode(elem, namespaceStack, displayLen)
						find_special = True
					elif     len(name) > 6 \
					     and name[:6] == "signal":
						globalWriteSignals += write_methode(elem, namespaceStack, displayLen)
						find_special = True
				if find_special == False:
					globalWrite += write_methode(elem, namespaceStack, displayLen)
			if globalWriteProperties != "":
				file.write('<h2>Properties:</h2>\n')
				file.write('<pre>\n');
				file.write(globalWriteProperties);
				file.write('</pre>\n')
				file.write('<br/>\n')
			if globalWriteSignals != "":
				file.write('<h2>Signals:</h2>\n')
				file.write('<pre>\n');
				file.write(globalWriteSignals);
				file.write('</pre>\n')
				file.write('<br/>\n')
			if globalWrite != "":
				file.write('<h2>Synopsis:</h2>\n')
				file.write('<pre>\n');
				file.write(globalWrite);
				file.write('</pre>\n')
				file.write('<br/>\n')
	
	# generate herirage list :
	if element.get_node_type() == 'class':
		parentAll = element.get_parents()
		debug.verbose("parrent of " + element.get_name() + " : " + str(parentAll))
		child = module.get_whith_specific_parrent(element.get_displayable_name(), )
		if    len(parentAll) != 0 \
		   or len(child) != 0:
			file.write('<h2>Object Hierarchy:<h2>\n')
			file.write('<pre>\n');
			level = 0
			for parent in parentAll:
				for parentElem in parent:
					access = ""
					if parentElem['access'] == 'public':
						access = "+"
					elif parentElem['access'] == 'protected':
						access = "#"
					elif parentElem['access'] == 'private':
						access = "-"
					tmpLen = level * 7
					if tmpLen > 0:
						tmpLen -= 5
					file.write(white_space(tmpLen))
					if level != 0:
						file.write('+--> ')
					file.write(access)
					classPointer = module.get_element_with_name(parentElem['class'])
					if classPointer != None:
						link = classPointer.get_doc_website_page()
						link = node.get_doc_website_page_relative(currentPageSite, link)
						file.write('<a href="' + link + '">')
					file.write(html_encode(parentElem['class']))
					#debug.warning("nodeName " + html_encode(parentElem['class']) )
					if classPointer != None:
						file.write('</a>')
					
					file.write('<br/>')
				level += 1
			# write local class:
			tmpLen = level * 7
			if tmpLen > 0:
				tmpLen -= 5
			file.write(white_space(tmpLen))
			if level != 0:
				file.write('+--> ')
			file.write(element.get_displayable_name())
			file.write('<br/>')
			level += 1
			# all child not in application :
			for childElem in child:
				tmpLen = level * 7
				if tmpLen > 0:
					tmpLen -= 5
				file.write(white_space(tmpLen))
				if level != 0:
					file.write('+--> ')
				classPointer = module.get_element_with_name(childElem)
				if classPointer != None:
					link = classPointer.get_doc_website_page()
					link = node.get_doc_website_page_relative(currentPageSite, link)
					file.write('<a href="' + link + '">')
				file.write(childElem)
				if classPointer != None:
					file.write('</a>')
				
				file.write('<br/>')
				
			
			file.write('</pre>\n');
		
	
	if len(listBase) != 0:
		# display all functions :
		file.write('<h2>Detail:</h2>\n')
		allDetailDoc = ""
		lastDoc = ""
		for subElement in listBase:
			if subElement['node'].get_request_hidden() == True:
				continue
			if     'access' in subElement.keys() \
			   and subElement['access'] == 'private':
				continue
			file.write('<a id="' + str(subElement['node'].get_uid()) + '"/>')
			if     lastDoc != "" \
			   and subElement['node'].get_request_in_previous() == True:
				allDetailDoc += write_methode(subElement, namespaceStack, link = False)
			else:
				if lastDoc != "":
					allDetailDoc += '</pre>\n'
					allDetailDoc += lastDoc
					allDetailDoc += '<br/>\n'
					allDetailDoc += '<hr/>\n'
					file.write(allDetailDoc);
					allDetailDoc = ""
					lastDoc = ""
				allDetailDoc += '<h3>' + subElement['node'].get_name() + '</h3>'
				allDetailDoc += '<pre>\n'
				allDetailDoc += write_methode(subElement, namespaceStack, link = False)
				lastDoc = parse_doxygen(subElement['node'].get_doc()) + '\n'
		if lastDoc != "":
			allDetailDoc += '</pre>\n'
			allDetailDoc += lastDoc
			allDetailDoc += '<br/>\n'
			allDetailDoc += '<hr/>\n'
			file.write(allDetailDoc);
			allDetailDoc = ""
			lastDoc = ""
		
	if element.get_node_type() == 'enum':
		myElementList = element.get_enum_list()
		elementSize = 0
		for enumElement in myElementList:
			tmpLen = len(enumElement['name'])
			if tmpLen > elementSize:
				elementSize = tmpLen
		
		
		file.write('<h2>Value list</h2>\n')
		if len(myElementList) < 9:
			nbColumn = 1
		else:
			nbColumn = 3
		
		file.write('<ul>\n');
		file.write('<table class="enumeration-list"><tr>\n');
		nbCol = 0
		isFirst = True
		for enumElement in myElementList:
			if isFirst == True:
				file.write('<tr>\n');
			isFirst = False
			file.write('<td><a href="#' + enumElement['name'] + '">' + enumElement['name'] + '</a></td>')
			nbCol += 1
			if nbCol == nbColumn:
				nbCol = 0
				file.write('</tr>\n');
				isFirst = True
		if isFirst == False:
			file.write('</tr>\n');
		file.write('</table>\n');
		file.write('</ul>\n');
		
		file.write("<h2>Detail:</h2>\n")
		isFirst = True
		for enumElement in myElementList:
			if isFirst == False:
				file.write('<hr/>\n');
			isFirst = False
			file.write('<h3><a id="' + enumElement['name'] + '"/>' + enumElement['name'] + '</h3>')
			file.write('<pre>\n')
			file.write(enumElement['name'] + white_space(elementSize-len(enumElement['name'])) + ' = <span class="code-type">' + enumElement['value'] + '<span>')
			file.write('</pre>\n')
			if enumElement['doc'] != "":
				file.write(parse_doxygen(enumElement['doc']));
		
	if element.get_node_type() == 'union':
		file.write("TODO : the page ...");
	
	file.write(footer)
	file.close();
	




def generate(my_lutin_doc, outFolder) :
	my_doc = my_lutin_doc.get_base_doc_node()
	tools.copy_file(tools.get_current_path(__file__)+"/theme/base.css", outFolder+"/base.css")
	tools.copy_file(tools.get_current_path(__file__)+"/theme/menu.css", outFolder+"/menu.css")
	# create common header
	generic_header  = '<!DOCTYPE html>\n'
	generic_header += '<html>\n'
	generic_header += '<head>\n'
	generic_header += '	<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">\n'
	generic_header += '	<title>' + my_doc.get_name() + ' Library</title>\n'
	generic_header += '	<link rel="stylesheet" href="base.css">\n'
	generic_header += '	<link rel="stylesheet" href="menu.css">\n'
	generic_header += '</head>\n'
	generic_header += '<body>\n'
	generic_header += '	<div class="navbar navbar-fixed-top">\n'
	generic_header += '		<div class="container">\n'
	if my_doc.get_node_type() == 'library':
		generic_header += '			<h1><a href="index.html">' + my_doc.get_name() + ' library</a></h1>\n'
	else:
		generic_header += '			<h1><a href="index.html">' + my_doc.get_name() + '</a></h1>\n'
	if my_lutin_doc.get_website_sources() != '':
		generic_header += '			<h4><a href="' + my_lutin_doc.get_website_sources() + '">&nbsp;&nbsp;&nbsp;[ sources ]</a></h4>\n'
	generic_header += '<h3>API:</h3>'
	generic_header += '			<div id="menu">\n'
	#generic_header += '				<h2>' + my_doc.moduleName + '</h2>\n'
	generic_header += generate_menu(my_doc)
	#generic_header += '				<h3> </h3>\n'
	generic_header += '			</div>\n'
	# TODO : add Generic doc main point.
	if len(my_lutin_doc.list_doc_file) > 0:
		docList = ""
		for docInputName,outpath in my_lutin_doc.list_doc_file:
			outputFileName = outFolder + "/" + outpath.replace('/','_') +".html"
			outputFileName = outputFileName.split('/')[-1]
			name = outputFileName.split('_')[-1][:-5]
			if name == "index":
				continue
			docList += '<ul class="niveau1">'
			docList += '<li><a href="' + outputFileName + '">' + capitalise_first_letter(camel_case_decode(name)) + '</a></li>\n'
			docList += '</ul>'
		if docList != "":
			generic_header += '<h3>Documentation:</h3>'
			generic_header += '<div id="menu">\n'
			generic_header += docList
			generic_header += '</div>\n'
	# TODO : add Tutorial doc main point.
	if len(my_lutin_doc.list_tutorial_file) > 0:
		tutorialList = ""
		for docInputName,outpath in my_lutin_doc.list_tutorial_file:
			outputFileName = outFolder + "/" + outpath+".html"
			outputFileName = outputFileName.split('/')[-1]
			name = outputFileName.split('_')[-1][:-5]
			if name == "index":
				continue
			tutorialList += '<ul class="niveau1">'
			tutorialList += '<li><a href="tutorial_' + outputFileName + '">' + capitalise_first_letter(camel_case_decode(name)) + '</a></li>\n'
			tutorialList += '</ul>'
		if tutorialList != "":
			generic_header += '<h3>Tutorials:</h3>'
			generic_header += '<div id="menu">\n'
			generic_header += tutorialList
			generic_header += '</div>\n'
	
	
	localWebsite = my_lutin_doc.get_website()
	# add other libs entry point :
	allModule = module.get_all_module()
	if len(allModule) != 1:
		generic_header += '<br/>'
		generic_header += '<h3>Associate libraries:</h3>'
		generic_header += '<div id="menu">\n'
		for modd in allModule:
			if modd.type == 'application':
				continue
			if modd.name == my_lutin_doc.name:
				continue
			generic_header += '<ul class="niveau1">'
			link = node.get_doc_website_page_relative(localWebsite, modd.get_website())
			debug.debug("link = " + str(link) + " << " + localWebsite + " !! " + str(modd.get_website()))
			if     len(link) != 0 \
			   and link[-1] != "/":
				link += "/"
			generic_header += '<li><a href="' + link + 'index.html">' + modd.name + '</a></li>\n'
			generic_header += '</ul>'
		generic_header += '</div>\n'
	generic_header += "<br/>\n"
	generic_header += "<br/>\n"
	generic_header += "<br/>\n"
	generic_header += "<br/>\n"
	generic_header += "<br/>\n"
	generic_header += "<br/>\n"
	generic_header += "		</div>\n"
	generic_header += "	</div>\n"
	generic_header += "	<div class=\"container\" id=\"content\">\n"
	
	generic_footer  = "	</div>\n"
	googleData = tools.file_read_data("google-analytics.txt")
	if googleData != "":
		debug.info("insert Google analytics Data")
		generic_footer += googleData
	generic_footer += "</body>\n"
	generic_footer += "</html>\n"
	
	# create index.hml:
	generate_stupid_index_page(outFolder, generic_header, generic_footer, my_lutin_doc)
	
	# create the namespace index properties:
	generate_page(outFolder, generic_header, generic_footer, my_doc, name_lib=my_lutin_doc.name)
	
	for iii in range(0, len(my_lutin_doc.list_tutorial_file)) :
		docInputName,outpath = my_lutin_doc.list_tutorial_file[iii]
		
		debug.print_element("tutorial", my_lutin_doc.name, "<==", docInputName)
		if outpath[0] == '/':
			outpath = outpath[1:]
		outputFileName = os.path.join(outFolder, outpath.replace('/','_') + ".html")
		debug.debug("output file : " + outputFileName + " out path=" + outFolder + " baseName=" + outpath)
		tools.create_directory_of_file(outputFileName)
		name = outputFileName.split('_')[-1][:-5]
		inData = tools.file_read_data(docInputName)
		if inData == "":
			continue
		outData = generic_header
		localHeader = ""
		localHeader += "=?=" + camel_case_decode(name) + "=?=\n___________________________\n"
		if iii != 0:
			previousName, previousOutpath = my_lutin_doc.list_tutorial_file[iii-1]
			previousName = previousName.split('_')[-1][:-3]
			previousOutpath = previousOutpath.split('/')[-1]
			localHeader += "[left][tutorial[" + previousOutpath + " | Previous: " + capitalise_first_letter(camel_case_decode(previousName)) + "]][/left] "
		if iii != len(my_lutin_doc.list_tutorial_file)-1:
			nextName, nextOutpath = my_lutin_doc.list_tutorial_file[iii+1]
			nextName = nextName.split('_')[-1][:-3]
			nextOutpath = nextOutpath.split('/')[-1]
			localHeader += " [right][tutorial[" + nextOutpath + " | Next: " + capitalise_first_letter(camel_case_decode(nextName)) + "]][/right]"
		localHeader += "\n"
		outData += codeBB.transcode(localHeader)
		#debug.info(localHeader)
		if docInputName[-2:] == "bb":
			outData += codeBB.transcode(inData)
		elif docInputName[-2:] == "md":
			outData += codeMarkDown.transcode(inData)
		outData += genericFooter
		tools.file_write_data(outputFileName, outData)
	
	for docInputName,outpath in my_lutin_doc.list_doc_file :
		debug.print_element("doc", my_lutin_doc.name, "<==", docInputName)
		outputFileName = outFolder + outpath + ".html"
		debug.debug("output file : " + outputFileName)
		tools.create_directory_of_file(outputFileName)
		inData = tools.file_read_data(docInputName)
		if inData == "":
			continue
		outData = generic_header
		if docInputName[-2:] == "bb":
			outData += codeBB.transcode(inData)
		elif docInputName[-2:] == "md":
			outData += codeMarkDown.transcode(inData)
		outData += generic_footer
		tools.file_write_data(outputFileName, outData)




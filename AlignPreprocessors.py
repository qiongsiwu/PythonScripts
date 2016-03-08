# Script to align indentations of preprocessing statements. 
#
# Lexemes
# The following types of lexemes are defined:
# 	For comments :
#		- BEGIN_ONE_LINE_COMMENT: '//'	
#		- BEGIN_MULTI_LINE_COMMENT:'/*'	
#       - END_MULTI_LINE_COMMENT: '*/'	
#	For new line:
#		- '\n'	NEW_LINE
#	For preprocessor:
#		- BEGIN_MOD_PREPROCESSOR: '#if\s*'
#       - BEGIN_DEFN_PREPROCESSOR: '#ifdef' or #ifndef
#		- CONTINUE_PREPROCESSOR: 
#			'#elif' or '#else' or '#include' or '#define' or 
#           'undef' or 'error' 
#		- END_PREPROCESSOR: '#endif'		
#    
# Rules:
# 1. Comments are skipped. C++ does not support nested comments. So it is
#    not supported. 
# 2. BEGIN_MOD_PREPROCESSOR increases the indentation level of all preprocessing
#    statements before the next closest END_PREPROCESSOR by 1. 
# 3. BEGIN_DEFN_PREPROCESSOR uses the same level of indentation same as 
#    BEGIN_PREPROCESSOR 
# 4. CONTINUE_PREPROCESSOR uses the same level of indentation same as 
#    BEGIN_PREPROCESSOR
# 5. END_PREPROCESSOR: if the current indentation block is a definition preprocessor, 
#    keep the current indentation level. If the current indentaiton block is
#    a mod preprocessor, decrease indentation level. 
#
# TAB is hardcoded to 3 spaces. 
#
# See http://www.cprogramming.com/reference/preprocessor/ for the list
# of preprocessing directives.


import collections
import re 
import sys
import os

Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

# Overall scanner states to skip comments
INITIAL = 0
IN_ONE_LINE_COMMENT = 1
IN_MULTI_LINE_COMMENT = 2

# States for preprocessors
OUT = 0; 
IN_DEFN = 1; 
IN_MOD = 2; 

TAB = '   '

def tokenize(code):
	token_specification = [
		('BEGIN_ONE_LINE_COMMENT', r'//.*'),   	
		('BEGIN_MULTI_LINE_COMMENT', r'/\*'),   
		('END_MULTI_LINE_COMMENT', r'\*/'), 
		('BEGIN_DEFN_PREPROCESSOR', r'#\s*if(def|ndef)\s+'),	
		('BEGIN_MOD_PREPROCESSOR', r'#\s*if\s+'), 					
		('CONTINUE_PREPROCESSOR', \
			r'#\s*(elif|else|include|define|undef|error)'),
		('END_PREPROCESSOR', r'#\s*endif'),
		('NEW_LINE', r'\n'),
		('SKIP', r'.'), 						#skip everything else
	]	
	state = INITIAL
	pp_state_stack = []
	tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
	current_pp_indent = 0;
	line_num = 1
	line_start = 0
	for mo in re.finditer(tok_regex, code):
		kind = mo.lastgroup
		value = mo.group(kind)
		if kind == 'BEGIN_ONE_LINE_COMMENT':
			if state == INITIAL or state == IN_ONE_LINE_COMMENT:
				state = IN_ONE_LINE_COMMENT
		elif kind == 'BEGIN_MULTI_LINE_COMMENT':
			if state == INITIAL:
				state = IN_MULTI_LINE_COMMENT
		elif kind == 'END_MULTI_LINE_COMMENT':
			if state == IN_MULTI_LINE_COMMENT:
				state = INITIAL
		elif kind == 'NEW_LINE':
			if state == IN_ONE_LINE_COMMENT:
				state = INITIAL
			line_start = mo.end()
			line_num += 1
		elif kind == 'SKIP':
			pass
		else:
			if state == INITIAL:
				column = mo.start() - line_start
				if kind == 'BEGIN_DEFN_PREPROCESSOR':
					pp_state_stack.append(IN_DEFN)
					yield Token(kind, current_pp_indent - 1, line_num, column)
				elif kind == 'BEGIN_MOD_PREPROCESSOR':
					pp_state_stack.append(IN_MOD)
					current_pp_indent += 1
					yield Token(kind, current_pp_indent - 1, line_num, column)				
				elif kind == 'CONTINUE_PREPROCESSOR':
					yield Token(kind, current_pp_indent - 1, line_num, column)
				elif kind == 'END_PREPROCESSOR':
					yield Token(kind, current_pp_indent - 1, line_num, column)
					curr_pp_state = pp_state_stack.pop()
					if curr_pp_state == IN_MOD:
						current_pp_indent -= 1

def add_tab_to_beginning_of_line(line, num_tabs):
	line = TAB * num_tabs + line
	return line

def ProcessThisFile(fileaddress):
	f = open(fileaddress, 'r')
	code = f.read()
	f.close()
	f = open(fileaddress, 'r')
	codebyline = f.readlines()
	f.close()	
	preprocessor_tokens = tokenize(code)
	for token in preprocessor_tokens:
		codebyline[token[2]-1] = add_tab_to_beginning_of_line(    \
								 codebyline[token[2]-1].lstrip(), \
								 token[1])
	f = open(fileaddress, 'w')
	f.writelines(codebyline)
	f.close()	
	
def main(): 
	if len(sys.argv) != 2:
		print("Please indicate file to produce")
		return
	fileaddress = sys.argv[1]
	print("Fixing file " + fileaddress)
	ProcessThisFile(fileaddress)
	print("Finished!")

if __name__ == "__main__":
	main()


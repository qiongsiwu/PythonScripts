import collections
import re 
import sys
import os

Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

INITIAL = 0
IN_ONE_LINE_COMMENT = 1
IN_MULTI_LINE_COMMENT = 2

TAB = '   '

def tokenize(code):
	token_specification = [
		('BEGIN_ONE_LINE_COMMENT', r'//.*'),   	
		('BEGIN_MULTI_LINE_COMMENT', r'/\*'),   
		('END_MULTI_LINE_COMMENT', r'\*/'), 
		('BEGIN_PREPROCESSOR', r'#\s*if(ndef|def)?'), 
		('CONTINUE_PREPROCESSOR', r'#\s*(elif|else|include|define|undef)'),
		('END_PREPROCESSOR', r'#\s*endif'),
		('NEW_LINE', r'\n'),
		('SKIP', r'.'),     #skip everything else
	]	
	state = INITIAL
	tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
	current_pp_indent = 0;
	line_num = 1
	line_start = 0
	for mo in re.finditer(tok_regex, code):
		kind = mo.lastgroup
		value = mo.group(kind)
		if kind == 'BEGIN_ONE_LINE_COMMENT':
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
				if kind == 'BEGIN_PREPROCESSOR':
					current_pp_indent += 1
					yield Token(kind, current_pp_indent - 1, line_num, column)
				elif kind == 'CONTINUE_PREPROCESSOR':
					yield Token(kind, current_pp_indent - 1, line_num, column)
				elif kind == 'END_PREPROCESSOR':
					yield Token(kind, current_pp_indent - 1, line_num, column)
					current_pp_indent -= 1	


def add_tab_to_beginning_of_line(line, num_tabs):
	line = TAB * num_tabs + line #line will not be changed if num_tabs < 0
	return line

def ProcessThisFile(fileaddress):
	print(fileaddress)	
	f = open(fileaddress, 'r')
	code = f.read()
	f.close()
	f = open(fileaddress, 'r')
	codebyline = f.readlines()
	f.close()	
	preprocessor_tokens = tokenize(code)
	for token in preprocessor_tokens:
		print("Fixing line: " + str(token[2]))
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
	fileaddress = os.getcwd() + '/' + sys.argv[1]
	ProcessThisFile(fileaddress)

if __name__ == "__main__":
	main()


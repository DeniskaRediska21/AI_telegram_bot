import re

def insert_backslash(text):
   return re.sub(r'([^a-zA-Z\n `])', r'\\\1', text)


def split_text_by_spans(text, spans):
    sections = []
    
    for start, end in spans:
        section = text[start:end]

    return sections

def apply_function_to_every_other_instance(arr, func):
   return [func(x) if i % 2 == 0 else x for i, x in enumerate(arr)]

def format_for_markdown(text):


    search = [x.span() for x in re.finditer('(\`\`\`.*?\`\`\`)',text,flags = re.DOTALL)]

    if len(search)>0:
        for i in range(len(search)-1):
            search.insert(i+1,(search[i][1]+1 , search[i+1][0]-1))

        search.insert(0, (0,max(0,search[0][0]-1)))
        search.append((min(search[-1][1]+1,len(text)) , len(text)))
    else:
        search = [(0,len(text))]


    sections = []

    for start, end in search:
        sections.append(text[start:end])

    sections= apply_function_to_every_other_instance(sections,insert_backslash)
    sections = ''.join(sections)
    return sections

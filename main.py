import xml.etree.ElementTree as ET
import json
import os
import glob
from datetime import datetime, timezone
from urlextract import URLExtract
from text_summarizer import summarize
import requests
from bs4 import BeautifulSoup

extractor = URLExtract()


def get_time():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def parse_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root


def text_from_section(section):
    text = section.find('title').text+'\n'
    for i in section:
        if i.tag == 'p':
            for j in i.itertext():
                text += j.strip().replace('/\n', '/').replace('_\n', '_').replace('-\n', '-').replace(':\n', ':').replace('\n', ' ')
            text += "\n\n"
        elif i.tag == 'sec':
            text += text_from_section(i)
    return text


def get_spec_version():
    return "https://w3id.org/ieee/ieee-2791-schema/2791object.json"


def get_provenance(front, body, back, creator):
    provenance = {}
    provenance['name'] = front.find('article-meta').find('title-group').find('article-title').text
    provenance['version'] = '2.0'
    provenance['license'] = 'http://creativecommons.org/licenses/by/4.0/'
    provenance['created'] = get_time()
    provenance['modified'] = get_time()
    affiliations = []
    contributors = []

    curator = {'name': creator[0],
               'email': creator[1],
               'affiliation': creator[2],
               'contribution': ['curatedBy']}
    contributors.append(curator)

    for affiliation in front[1][1]:
        if affiliation.tag == 'aff':
            affiliations.append(affiliation)

    for author in front[1][1]:
        if author.tag == 'contrib':
            contributor = {}
            contributor['email'] = ''
            contributor['orcid'] = ''
            contributor['name'] = author[0].text
            author_affiliation = ""
            for i in range(1, len(author)):
                if author[i].tag == 'email':
                    contributor['email'] = ''
                if author[i].tag == 'xref':
                    author_affiliation += author[i].text + affiliations[int(author[i].text)][1].text
            contributor['affiliation'] = author_affiliation
            contributor['contribution'] = ['authoredBy']
            contributors.append(contributor)

    provenance['contributors'] = contributors


    return provenance

def get_usability(front, body, back):
    abstract = front.find('article-meta').find('abstract')[0].text
    usability = abstract.split('. ')
    return usability


def get_io(front, body, back):
    return {}


def get_description(front, body, back):
    description = {}

    keywords = []
    kwd_groups = front.find('article-meta').findall('kwd_groups')
    if len(kwd_groups) > 0:
        for keyword in kwd_groups:
            keywords.append(keyword.text)
    else:
        keywords.append(summarize(front.find('article-meta').findall('abstract')[0].text))
    description['keywords'] = keywords

    pipeline_steps = []
    for i in body.findall('sec'):
        if 'methods' in i.find('title').text.lower():
            methods = i
            break
    count = 0
    for i in methods.findall('sec'):
        links = extractor.find_urls(text_from_section(i))
        if len(links) > 0:
            count += 1
            step = {'step_number': count,
                    'name': i.find('title').text,
                    'description': text_from_section(i),
                    'versions': '',
                    'input_list': {'filename': '',
                                   'access_time': get_time(),
                                   'uri': links[0],
                                   'sha1_checksum': ''},
                    'output_list': {'filename': '',
                                    'access_time': get_time(),
                                    'uri': '',
                                    'sha1_checksum': ''}
                    }
            pipeline_steps.append(step)
    description['pipeline_steps'] = pipeline_steps

    return description


def get_execution(front, body, back):
    execution = {'external_data_endpoints': [], 'environment_variables': {}}

    scripts = []
    for i in body.findall('sec'):
        if 'requirements' in i.find('title').text.lower():
            text = text_from_section(i)
            links = extractor.find_urls(text)
            for link in links:
                script = {'filename': link.split('/')[-1],
                          'uri': link,
                          'access_time': '',
                          'sha1_checksum': ''}
                scripts.append(script)
            break
    execution['scripts'] = scripts

    software_prerequisites = []
    for i in body.findall('sec'):
        if ('methods' in i.find('title').text) or ('Methods' in i.find('title').text):
            text = text_from_section(i)
            print(text)
            links = extractor.find_urls(text)
            print(links)
            for link in links:
                script = {'filename': link.split('/')[-1],
                          'uri': link,
                          'access_time': '',
                          'sha1_checksum': ''}
                software_prerequisites.append(script)
            break
    execution['software_prerequisites'] = software_prerequisites

    return execution


def get_extension(front, body, back):
    return {}


def get_error(front, body, back):
    return {}


def get_parametric(front, body, back):
    return []


def create_bco(name, maker):
    maker = ['Aditya Lahiri', 'adityalahiri06@gmail.com', 'George Washington University']
    root = parse_xml(name)
    front = root[0]
    body = root[1]
    back = root[2]
    bco = {'object_id': '',
           'etag': '',
           'spec_version': get_spec_version(),
           'provenance_domain': get_provenance(front, body, back, maker),
           'usability_domain': get_usability(front, body, back),
           'description_domain': get_description(front, body, back),
           'execution_domain': get_execution(front, body, back),
           'extension_domain': get_extension(front, body, back),
           'error_domain': get_error(front, body, back),
           'parametric_domain': get_parametric(front, body, back),
           'io_domain': get_io(front, body, back)}

    with open(name[0:-8]+'.json', 'w') as f:
        json.dump(bco, f, indent=4)
    print(bco)


def parse_papers(path=None):
    maker = ['Aditya Lahiri', 'adityalahiri06@gmail.com', 'George Washington University']
    os.system('java -cp cermine-impl-1.13-jar-with-dependencies.jar pl.edu.icm.cermine.ContentExtractor -path ' + path)
    if path:
        for filename in glob.glob(os.path.join(path, '*.cermxml')):
            create_bco(filename, maker)
    else:
        for filename in glob.glob('*.json'):
            pass
            #create_bco(filename, maker)


parse_papers('pdfs')
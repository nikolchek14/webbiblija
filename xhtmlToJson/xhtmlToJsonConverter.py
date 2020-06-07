import xml.etree.ElementTree as ET
import json

'''
kniga
    naslov
    podnaslov
    kratenka
    voved: 
        text: paragrafi[]
    glavi:
        stihoj: 
            podnaslov
            text
            footnoti
            referenci
'''

knigi = [];

metaKnigi = {}
metaFut = {}

tagPrefix='{http://www.w3.org/1999/xhtml}'
nav = ET.parse('../resources/xhmls/nav.xhtml')
nov = ET.parse('../resources/xhmls/NovZavet.xhtml')
star = ET.parse('../resources/xhmls/StarZavet.xhtml')
fut = ET.parse('../resources/xhmls/Futnoti.xhtml')

def tag(tag):
    return '%s%s' % (tagPrefix, tag)

def clas(elem, clas):
    return elem.attrib.get('class') == clas

for elem in nav.iter():
    if(elem.tag == tag('a') and elem.attrib.get('href').startswith('Kniga')):
        metaKnigi[elem.attrib.get('href')] = {'kratko_ime':elem.text}

for elem in fut.iter():
    if(elem.tag == tag('aside') and elem.attrib.get('class') == 'futnota_tekst'):
        metaFut[elem.attrib.get('id')] = elem.find(tag('span')).text

for elem in nov.iter():
    if(elem.tag == tag('a') and elem.attrib.get('href').startswith('Kniga')):
        metaKnigi[elem.attrib.get('href')]['celo_ime'] = elem.text[:elem.text.find('|')].strip()
        metaKnigi[elem.attrib.get('href')]['kratenka'] = elem.text[elem.text.find('|')+1:].replace('(','').replace(')','').strip()

for elem in star.iter():
    if(elem.tag == tag('a') and elem.attrib.get('href').startswith('Kniga')):
        metaKnigi[elem.attrib.get('href')]['celo_ime'] = elem.text[:elem.text.find('|')].strip()
        metaKnigi[elem.attrib.get('href')]['kratenka'] = elem.text[elem.text.find('|')+1:].strip().replace('(','').replace(')','').strip()

for key, value in metaKnigi.items():
    tree = None
    tree = ET.parse('../resources/xhmls/'+key)
    kniga = {};
    kniga['voved'] = []
    kniga['glavi'] = []
    kniga['kratko_ime'] = value.get('kratko_ime')
    kniga['celo_ime'] = value.get('celo_ime')
    kniga['kratenka'] = value.get('kratenka')
    podnaslov = None
    megunaslov = None
    podnaslovReferenca = None
    stih = {}
    stihovi = []
    glava = {}
    futnoti = []
    referenci = []
    for elem in tree.iter():
        if(elem.tag == tag('h1')):
            naslov = elem.text if elem.text else elem.find(tag('a')).text
            kniga['naslov'] = naslov.strip()
            if(elem.find(tag('sup')) and elem.find(tag('sup')).attrib.get('class') == 'futnota_naslov'):
                kniga['naslov_futnota'] = {'futnota_id':elem.find(tag('sup')).attrib.get('id'), 'r_br':elem.find(tag('sup')).find(tag('a')).text}
        if(elem.tag == tag('h2')):
            kniga['podnaslov'] = elem.text
        if (elem.tag == tag('p') and clas(elem,'voved_tekst')):
            kniga['voved'].append(elem.text)
        if(elem.tag == tag('h4') and clas(elem,'podnaslov')):
            podnaslov = elem.text
        if(elem.tag == tag('h4') and clas(elem,'megunaslov')):
            megunaslov = elem.text
        if (elem.tag == tag('h4') and clas(elem, 'podnaslovReferenca')):
            podnaslovReferenca = elem.text
        if((elem.tag == tag('span') and clas(elem,'glava_broj')) or (elem.tag == tag('h4') and clas(elem,'psalm'))):
            stihovi = []
            glava = {}
            glava['stihovi'] = stihovi
            stih = {}
            futnoti = []
            referenci = []
            stihovi.append(stih)
            if(podnaslov):
                stih['podnaslov'] = podnaslov
            if (megunaslov and not elem.text.find('ПСАЛМ')>-1):
                stih['megunaslov'] = megunaslov
                megunaslov = None
            podnaslov = None
            if (podnaslovReferenca):
                stih['podnaslov_referenca'] = podnaslovReferenca
                podnaslovReferenca = None
            kniga['glavi'].append(glava)
            glava_broj = elem.text[elem.text.find('ПСАЛМ') + len('ПСАЛМ')+1:].strip() if elem.text.find('ПСАЛМ') > -1 else elem.text
            glava['r_br'] = glava_broj
            stih_broj = 1
        if (elem.tag == tag('sup') and clas(elem, 'stih_broj')):
            stih = {}
            futnoti = []
            referenci = []
            stihovi.append(stih)
            if(podnaslov):
                stih['podnaslov'] = podnaslov
            if (megunaslov):
                stih['megunaslov'] = megunaslov
            megunaslov = None
            podnaslov = None
            if (podnaslovReferenca):
                stih['podnaslov_referenca'] = podnaslovReferenca
                podnaslovReferenca = None
            stih_broj = elem.text
        if (elem.tag == tag('span') and clas(elem,'stih_tekst')):
            stih['r_br'] = stih_broj
            if (not stih.get('tekst')):
                stih['tekst'] = elem.text
            else:
                stih['tekst'] += str(elem.text)
        if (elem.tag == tag('sup') and clas(elem, 'futnota')):
            stih['futnoti'] = futnoti
            futnota = {}
            futnota['futnota_id'] = elem.attrib.get('id')
            futnota['r_br'] = elem.find(tag('a')).text
            futnota['mesto'] = len(stih.get('tekst'))
            futnota['tekst'] = metaFut[elem.attrib.get('id')]
            futnoti.append(futnota)
        if (elem.tag == tag('a')):
            link = elem
        if (elem.tag == tag('sub') and clas(elem, 'referenci')):
            stih['referenci'] = referenci
            referenca = {}
            referenca['referenca'] = elem.text.strip()

            referenci.append(referenca)
            if(link.find(elem.tag) == elem):
                referenca['meta_link'] = link.attrib.get('href')

    kniga['meta_fajl'] = key[:key.find('.xhtml')]
    knigi.append(kniga);
    with open('../resources/jsons/'+key[:key.find('.xhtml')]+'.json', 'w', encoding='utf-8') as outfile:
        json.dump(kniga, outfile, ensure_ascii=False, indent=4)

with open('../resources/jsons/Biblija.json', 'w', encoding='utf-8') as outfile:
    json.dump(knigi, outfile, ensure_ascii=False, indent=4)


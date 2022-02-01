

from openie import StanfordOpenIE
import fitz #pip install PyMuPDF
from wordcloud import WordCloud


oc_path = 'utils/common_occupations.txt'


properties = {
    'openie.affinity_probability_cap': 1 / 3,
    "openie.triple.strict":"false"
}

def get_triples(text):
    with StanfordOpenIE(properties=properties) as client:
        triples = client.annotate(text)
    return triples


def read_occupations(path):
    f = open(path)
    
    lines = f.readlines()
    lines = [line.lower().strip() for line in lines]
    return lines

def occ_found(occupations, text):
    arr = text.split(' ')
    for oc in occupations:
        if oc in arr:
            return True
    return False

def rel_contains(text):
    rels = ['is', 'was', 'were', 'has', 'had', 'will', 'would', 'be', 'been', 'his', 'her']
    for rel in rels:
        if rel in text:
            return True
    return False

def get_occupation_lines(text):
    lines = '. '.join([line for line in text.split('.') if occ_found(occupations, line)])
    return lines

def get_occupations_count(occupations, text):
    
    women_rel = []
    
    men_rel = []
    
    
    text = get_occupation_lines(text)
    knowledge_base = ''
    log = ''
    for line in text.split('.'):
        triples = get_triples(line)
        #print(triples)
        for triple in triples:
            #if(rel_contains(triple['relation'])):
            #print(triple)
            if occ_found(occupations, triple['object']):# or occ_found(occupations, triple['subject']):
                #print('FOUND1')
                if 'she' in triple['subject'].lower().split(' ') or 'her' in  triple['subject'].lower().split(' '):
                    women_rel.append(triple)
                    log += str(triple)+'\n'
                    knowledge_base += triple['object'] + ' ' + triple['subject'] + ' '
                    break
                if 'he' in triple['subject'].lower().split(' ') or 'his' in  triple['subject'].lower().split(' '):
                    men_rel.append(triple)
                    log += str(triple)+'\n'
                    knowledge_base += triple['object'] + ' ' + triple['subject'] + ' '
                    break
            if occ_found(occupations, triple['subject']):# or occ_found(occupations, triple['object']):
                #print('FOUND2')
                if 'she' in  triple['object'].lower().split(' ') or 'her' in  triple['object'].lower().split(' '):
                    women_rel.append(triple)
                    log += str(triple)+'\n'
                    knowledge_base += triple['object'] + ' ' + triple['subject'] + ' '
                    break
                if 'he' in triple['object'].lower().split(' ') or 'his' in  triple['object'].lower().split(' '):
                    men_rel.append(triple)
                    log += str(triple)+'\n'
                    knowledge_base += triple['object'] + ' ' + triple['subject'] + ' '
                    break
    if(len(men_rel) + len(women_rel) == 0):
        return 0, 0, knowledge_base
    return len(men_rel)/(len(men_rel)+len(women_rel))* 100, len(women_rel)/(len(men_rel)+len(women_rel))* 100, knowledge_base

occupations = read_occupations(oc_path)

"""# PERCENTAGE FINDER"""

def get_gender_score(text):
    paras = text.split('\n')
    
    
    male_words = []
    female_words = []
    all_words = []
    for i, para in enumerate(paras):
        para = para.replace(',', '')
        para = para.replace(';', '')
        para = para.replace('.', '')
        para = para.replace('!', '')
        para = para.replace('"', '')
        para = para.replace('\t', ' ')
        
        words = para.split(' ')
        mw = [word for word in words if word.lower() in ['male', 'males', 'boy', 'boys', 'man', 'men', 'husband', 'he', 'his', 'him', 'himself', 'brother', 'brothers', 'father', 'fathers', 'son', 'sons', 'grandfather'] ]
        fw = [word for word in words if word.lower() in ['female', 'females', 'girl', 'girls', 'woman', 'women', 'wife', 'she', 'her', 'hers', 'herself', 'sister', 'sisters', 'mother', 'mothers', 'daughter', 'daughters', 'grandmother' , 'grandma', 'grannie'] ]
        
        male_words.extend(mw)
        female_words.extend(fw)
        all_words.extend(words)



    #print(male_words)
    #print(female_words)
    male_score = len(male_words)*100/len(all_words)
    female_score = len(female_words)*100/len(all_words)
    male_per = len(male_words)/(len(male_words) + len(female_words)) * 100
    female_per = len(female_words)/(len(male_words) + len(female_words)) * 100
    
    return male_per, female_per, ' '.join(male_words + female_words)#, male_words, female_words

"""# PDF READER"""

def read_pdf(path):

    with fitz.open(path) as doc:
        text = ""
        for page in doc:
            text += page.getText()+"\n"
    return text

"""# WORD CLOUD"""

def get_word_cloud(text):
    word_cloud = WordCloud(width = 800, height = 800,
                    background_color ='white',
                    min_font_size = 10).generate(text)

    return word_cloud

def main(pdf_path, occ_path):
    
    occupations = read_occupations(occ_path)
    text = read_pdf(pdf_path)
    
    global men, women, words, men_per, women_per ## global variables for sharing purposes.
    
    
    men, women, words = get_gender_score(text)
    men_per, women_per, occ_words = get_occupations_count(occupations, text)
    global is_balanced 
    
    if(women >= 40 and women_per >= 40):
        is_balanced = True
    elif(women >= 50 and women_per > 30):
        is_balanced = True
    else:
        is_balanced = False
        
    ## is_balanced determines if the document is gender balanced or not

    word_cloud = get_word_cloud(occ_words + ' ' + occ_words + ' ' + words)
    word_cloud.to_file('uploaded/word_cloud.png')
    return {
            "men" : round(men, 2),
            "women" : round(women, 2),
            "men_occ" : round(men_per, 2),
            "women_occ" : round(women_per, 2),
            "is_balanced" : is_balanced
        }


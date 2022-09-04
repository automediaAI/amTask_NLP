#########################
#### NLP using spaCy ####
#########################
# FEATURES --> 
## Named Entity Recognition (NER) Service using Spacy 
## Similarity detector for sentences or words, using Word Vectors in spaCy

# DOCUMENTATION -->
## NER Basics: https://spacy.io/usage/spacy-101#annotations-ner | https://spacy.io/usage/linguistic-features#named-entities | https://spacy.io/api/annotation#named-entities | Set entity if not recognized https://spacy.io/usage/linguistic-features#setting-entities 

## Similarity Basics: https://spacy.io/usage/spacy-101#vectors-similarity

#############
# NOTES

##############

# Work Pending 
## Create a similary function that tests similarity of headlines and returns T/F with basic threshold 
## Take optional threshold value too  

# Known Issues 
## NER - For PERSON only works with title case 'Elon Musl' not  'ELon Musk' or 'elon musk' - seems a spaCy limitation or of the model, as works for GPE --> try LG model 

# Extra Work 
## NER - Get confidence for NER (?) possible? 
## NER - See if any measure of weight or importance of entity ?
## Allow mutliple language support by getting more models from https://spacy.io/usage/models#languages 

#############

from importlib.metadata import entry_points # Not sure? Ask Nitin
import spacy
# from spacy import displacy #Used to display entity in browser, not used

#Main spaCy language model with NER support to process text. Dont use SM since doesnt have word vectors
nlp_en = spacy.load("en_core_web_md") # English medium model 
nlp_trf = spacy.load("en_core_web_trf") # Transformer based model, uses GPU so heavy

## Following types ie labels of entities are ignored by the code to keep focus on important types
ner_ban_list = [
    "PERCENT",
    "MONEY",
    "QUANTITY",
    "ORDINAL",
    "CARDINAL",
    "DATE",
    "TIME"
]

###### Main function to call spaCy and get Named Entities as keywords, ignoring those from list above  ######
def nlp_ner(txt_in):
    # print(txt_in)
    doc = nlp_trf(txt_in) #Has sequence of tokens and all annotations 
    ents_list = list(doc.ents) #Getting entities of tokens and storing in list 

    ## Adding text of each entity 
    ents_list_str = []
    for i in ents_list:
        if i.label_ not in ner_ban_list: 
            ents_list_str.append(i.text)


    ## Loop to add entity as separate list with details 
    ents_list_withTitle = []
    for ent in ents_list:
       if ent.label_ not in ner_ban_list: 
        ents_list_withTitle.append({
                "entity_word": ent.text,
                "entity_type": ent.label_,
            })

    ## Loop to add entity details to each word
    word_list = [] #Empty list where we will append text and ent
    for i in doc:
        # print ("Token word:", i.text, "| has vector:", i.has_vector, " norm:", i.vector_norm) # Testing to solve the person title case issue 
        if i.ent_iob == 3 and i.ent_type_ not in ner_ban_list: #Only interested in NER tokens AND not in Ban List 
            # print ("yes entiti")
            word_list.append({
                "word": i.text,
                "entity_exist": True,
                "entity_type": i.ent_type_,
                "ent_iob":i.ent_iob
            })

        ## This solves for the problem that entity could be split acorss multiple tokens. The IOB position tells us if token is part of another entity token. More here - https://spacy.io/usage/linguistic-features#accessing-ner
        elif i.ent_iob == 1 and i.ent_type_ not in ner_ban_list:
            if word_list[-1]["ent_iob"] == 3:
                word_list[-1]["word"] = word_list[-1]["word"] + " " +i.text #adding text back to original token

        else: #When not a entity, or entity is in ban list
            word_list.append({
                "word": i.text,
                "entity_exist": False, 
                "ent_iob":i.ent_iob
            })

    return ({
        ## IMPORTANT - FINAL OUTPUT DICT
        "NER_list":ents_list_str, # List of entities in Str format 
        "NER_list_withTitle": ents_list_withTitle,
        "text_original":txt_in, # text as is 
        "text_NERannotated": word_list #text with entity or not  KILLING FOR NOW TILL WE FIND A USE CASE
    })


### Similarity Function to compare text like headlines etc
#Manually declaring threshold if not entered. Need to keep playing to find best
# similarity_threshold = 0.9 #Seems decent at first try
similarity_threshold = 0.85 #For news 
def nlp_similarity(txt_control, txt_variant, threshold=similarity_threshold): #Control is what its being tested against, variant is what is being tested
    doc1 = nlp_en(txt_control)
    doc2 = nlp_en(txt_variant)

    similarity_score = doc1.similarity(doc2)
    if similarity_score >= threshold: 
        return True
    else:
        return False


## TESTING SIMILARITY 
# test1 = "Whats going on"
# test1 = "Joe goes to China"
# test2 = "Joe talks about China"

# # Live news article https://ground.news/article/lindsey-graham-predicts-riots-if-trump-is-prosecuted-over-classified-documents_ad23c3 
# test1 = "Sen. Lindsey Graham said if Trump is prosecuted for mishandling classified information 'there will be riots in the streets'"
# test2 = "Lindsey Graham Comes Close to Criminal Threats: 'If Trump is Prosecuted, There Will Be Riots in the Streets'"
# test2 = "Graham predicts ‘riots in the streets’ if Trump prosecuted over classified docs"

# print(nlp_similarity(test1, test2,.80))


## TESTING NER##

# x_empty = ("")
# # print(nlp_ner(x_empty))

# y = "Bank of America issued their annual report"
# y = "The is how china works with elon musk"
# print (nlp_ner(y))

# x = ("""When Sebastian Thrun started working on self-driving cars at Google in 2007,
#     few people outside of the company took him seriously. “I can tell you very senior 
#     CEOs of major American car companies would shake my hand and turn away because I 
#     wasn’t worth talking to,” said Thrun, now the co-founder and CEO of online higher 
#     education startup Udacity, in an interview with Recode earlier this week.

#     The Mona Lisa and the Statue of David were on display in the MOMA New York.

#     COVID-19 is a devastating virus currently ravaging the world.
    
#     A little less than a decade later, dozens of self-driving startups have cropped up 
#     while automakers around the world clamor, wallet in hand, to secure their place in 
#     the fast-moving world of fully automated transportation.""")
# print (nlp_ner(x))





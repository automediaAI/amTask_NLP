
##############
#### ML Services on Airtable ####
#################
## Pulls data from airtable, runs ML servies like NER, Summarizer and puts output back. Also has option to pull from a local file instead of airtable for future proof  ##
## !!! IMP !!! - Other services likle SSML creator will use output, this service is strictly for the ML work 
##############
## WORK ITEMS 
# . Finish summarizer 
# . Setup to run on local data file
# . Have commended off small thing below in NER to remove source name from NER 

## Future 
## . Figure out use of the NER?? Input to SSML creator? Or pull images? 
## . Setup to pull from a DB (per new structure)
#############

## Declarations 
from genericpath import exists
import os
import ast #to covert string to list 
from pyairtable import Table
import json
import uuid # Used to give ID to article to avoid duplicate headline 
import pandas as pd # Used to dedupe similar articles per UUIDs 
from amService_NLP import nlp_ner, nlp_similarity

## Airtable settings 
base_key = os.environ.get("PRIVATE_BASE_KEY")
table_name_news = os.environ.get("PRIVATE_TABLE_NAME_NEWSPAYLOAD") #What to pull
# table_producer = os.environ.get("PRIVATE_TABLE_NAME_PRODUCER")
api_key_airtable = os.environ.get("PRIVATE_API_KEY_AIRTABLE")
# airtable_producer = Airtable(base_key, table_producer, api_key_airtable)
# airtable_payload_news = Airtable(base_key, table_name_news, api_key_airtable)
airtable_payload_news = Table(api_key_airtable, base_key, table_name_news)


######### DATA UPLOAD FUNCTIONS #########

#Uploads single json, or list to data_output of record ID as given
def uploadData(inputDictList, recToUpdate):
	recID = recToUpdate
	if isinstance(inputDictList, dict):
		fields = {'output': json.dumps(inputDictList)}
		# fields = {'data_output': str(inputDictList)} #Seems if I do str thats same too
	else:
		fields = {'output': str(inputDictList)}
	airtable_payload_news.update(recID, fields)



########## NER FUNCTION ############

#Gets NER for Title and Content of all records in news article and uploads back.  
def updateNER():
	allRecords = airtable_payload_news.all()
	for i in allRecords:
		try: #In case have a prod payload or anything wrong 
			if "Prod_Ready" in i["fields"]: #Only working on prod ready ie checkboxed
			# if "test_Prod" in i["fields"]: #In testing phase using Test flag
				rec_ofAsked = i["id"]
				data_toUpload = [] #Empty list that gets remade 
				output_native = i["fields"]["output"] #Payload of data asked
				output_json = ast.literal_eval(output_native) #since List from airtable is in String

				for news_item in output_json:
					article_source = news_item['source_article']

					try:
						news_item['title_article']
						if news_item['title_article'] is not None and news_item['title_article'] != "":
							title_NER_output = nlp_ner(news_item['title_article'].strip())
						else:
							title_NER_output = [] #Empty dict to avoid tripping check below - CHECK LATER if any other issues
					except NameError:
						continue
					try:
						news_item['content_article']
						if news_item['content_article'] is not None and news_item['content_article'] != "":
							content_NER_output = nlp_ner(news_item['content_article'].strip())
						else:
							content_NER_output = [] 
					except NameError:
						continue
 
					## Nitin added, avoids source name in NER cause articles often have source name at end -- Ideal way to solve these is to remove these in advance using a text function 
					# if article_source in title_NER_output['NER_list']: ## Nitin added, avoids source name in NER 
					# 	title_NER_output.remove(article_source)
					## removing this bit for a little while since issue of where contnet is None. Also cause this doesnt happen that often. 
					# elif article_source in content_NER_output['NER_list']:
					# 	content_NER_output.remove(article_source)

					## Creating output to upload back 
					news_item['title_NER_output'] = title_NER_output #Getting title NER
					news_item['content_NER_output'] = content_NER_output #Also getting content NER 
					data_toUpload.append(news_item)

				# print ("Pre CMS Upload back .. ")	
				uploadData(data_toUpload, rec_ofAsked) #Just that bit updated  #Running into size issues
				print ("News upload to CMS done..")
		except Exception as e:
			print(e)
	print ("NER run complete")


########## SIMILARITY  FUNCTION ############
## Function uses similarity to compare each headline with others in list and assigns a UUID to unique stories. For similar ones its repeated
def attachSimilarityID(articleListIn):
	orgArticleList = articleListIn
	cleanArticleList = [] #Wtihout duplicate headlines 
	for news_item in orgArticleList:
		news_header_control = news_item['title_article'] #Headline to test 
		if 'title_uniqueID' in news_item: #If already has a UUID then skip it 
			continue
		else:
			news_item['title_uniqueID'] = str(uuid.uuid4())[:8] #Adding a UUID to this only using last 8
			for news_item_next in orgArticleList:
				news_header_variant= news_item_next['title_article']
				similarity_test = nlp_similarity(news_header_control, news_header_variant, 0.7) #Threshold of 70%
				if similarity_test is True:
					news_item_next['title_uniqueID'] = news_item['title_uniqueID']
	return orgArticleList

## Uses similarity function above, takes UUID into account and deletes duplicate records. Keeps first variant of duplicate article, not later ones
def returnUniqueArticles(articleListIn):
	allArticleList = attachSimilarityID(articleListIn) #Attaching UUIDs to each article per similarity 
	df = pd.DataFrame(allArticleList)
	uniqueArticleList = df.drop_duplicates(subset=['title_uniqueID']) #Deletes records with duplicate UUID, keeps first loses later ones
	return uniqueArticleList.to_dict('records') #Convert back from df to dict

## Function that uses functions above to get data from airtable, remove similar news based on title and uploads back
def removeSimilarHeadlines():
	allRecords = airtable_payload_news.all()
	for i in allRecords:
		try: #In case have a prod payload or anything wrong 
			if "Prod_Ready" in i["fields"]: #Only working on prod ready ie checkboxed
			# if "test_Prod" in i["fields"]: #In testing phase using Test flag
				rec_ofAsked = i["id"]
				output_native = i["fields"]["output"] #Payload of data asked
				output_json = ast.literal_eval(output_native) #since List from airtable is in String

				attachUniqueID = attachSimilarityID(output_json)
				onlyUniqueArticles = returnUniqueArticles(attachUniqueID)
			
				uploadData(onlyUniqueArticles, rec_ofAsked) #Just that bit updated 
				print ("Unique News upload to CMS done..")

		except Exception as e:
			print(e)
	print ("Headline Similarity run complete")



########## TASK FUNCTION ############
# Combines all functions above to run on entire data 

def task_runner():
	## Each function runs on all rows > uploads data back > nexts on runs on update data on all rows again 
	print ("Removing duplicate news items ...")
	removeSimilarHeadlines()
	print ("Adding NER to news content ...")
	updateNER()
	print (" ... NLP Functions complete")

task_runner()







######## TESTING ##########

## Testing NER 
# updateNER()

# TESTING SIMILARITY 
# removeSimilarHeadlines()

# Test Data 
# test_news = [{
# 	'source_API': 'newsAPI',
# 	'query_name': 'Health News US - NewsAPI',
# 	'source_article': 'Sky.com',
# 	'title_article': 'Faecal transplants to be offered to hundreds with antibiotic-resistant superbug - Sky News',
# 	'description_article': '',
# 	'url_article': 'https://news.sky.com/story/faecal-transplants-to-be-offered-to-hundreds-with-antibiotic-resistant-superbug-12685557',
# 	'urtToImage_article': 'https://e3.365dm.com/22/08/1600x900/skynews-health-poo-transplant_5881514.jpg?20220830192932',
# 	'publishedAt_article': '2022-08-31T01:30:43Z',
# 	'content_article': 'Hundreds of people with a hard-to-treat superbug are to be offered faecal transplants to tackle their infections.\r\nA faecal microbiota transplant (FMT) involves taking healthy bacteria "in a mixture … [+2957 chars]',
# 	'keywords_article': ['Sky News'],
# 	'keywords_info_article': [{
# 		'text': 'Sky News',
# 		'label': 'ORG'
# 	}]
# }, {
# 	'source_API': 'newsAPI',
# 	'query_name': 'Health News US - NewsAPI',
# 	'source_article': 'HuffPost',
# 	'title_article': '6 Signs You’re Grinding Your Teeth At Night (And What To Do About It) - HuffPost',
# 	'description_article': "Beyond toothaches, there are other common red flags that you're dealing with nighttime teeth grinding.",
# 	'url_article': 'https://www.huffpost.com/entry/signs-of-teeth-grinding_l_6307b72ee4b0f7df9bb7e34f',
# 	'urtToImage_article': 'https://img.huffingtonpost.com/asset/6307b8072200005e00b637d4.jpeg?ops=1200_630',
# 	'publishedAt_article': '2022-08-30T09:45:03Z',
# 	'content_article': 'From chipped teeth to tooth sensitivity, grinding your teeth at night can have serious consequences. \r\nNighttime is meant to be a period of peace and quiet restful evenings, pleasant dreams and rejuv… [+5238 chars]',
# 	'keywords_article': [],
# 	'keywords_info_article': []
# } , {
# 	'source_API': 'newsAPI',
# 	'query_name': 'Health News US - NewsAPI',
# 	'source_article': 'HuffPost',
# 	'title_article': '6000 Signs You’re Grinding Your Teeth At Night (And What To Do About It) - HuffPost',
# 	'description_article': "Beyond toothaches, there are other common red flags that you're dealing with nighttime teeth grinding.",
# 	'url_article': 'https://www.huffpost.com/entry/signs-of-teeth-grinding_l_6307b72ee4b0f7df9bb7e34f',
# 	'urtToImage_article': 'https://img.huffingtonpost.com/asset/6307b8072200005e00b637d4.jpeg?ops=1200_630',
# 	'publishedAt_article': '2022-08-30T09:45:03Z',
# 	'content_article': 'From chipped teeth to tooth sensitivity, grinding your teeth at night can have serious consequences. \r\nNighttime is meant to be a period of peace and quiet restful evenings, pleasant dreams and rejuv… [+5238 chars]',
# 	'keywords_article': [],
# 	'keywords_info_article': []
# }]


# print(attachSimilarityID(test_news)) #Testing just similar ID 
# print(returnUniqueArticles(test_news)) #Removes but on local dict 

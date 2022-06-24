
##############
#### Airtable Data Service for CMS - ALl Services ####
#################
## Feed it news, covid data. Pulls payload from airtable service output per correct service & pulls output and uploads data in correct format as needed.  ##
##############
## Ticket:  
#############

## Declarations 
import os
import ast #to covert string to list 
from pyairtable import Table
import json
from amService_NLP import ner_caller

# Airtable settings 
base_key = os.environ.get("PRIVATE_BASE_KEY")
table_name_news = os.environ.get("PRIVATE_TABLE_NAME_NEWSPAYLOAD") #What to pull
# table_producer = os.environ.get("PRIVATE_TABLE_NAME_PRODUCER")
api_key_airtable = os.environ.get("PRIVATE_API_KEY_AIRTABLE")
# airtable_producer = Airtable(base_key, table_producer, api_key_airtable)
# airtable_payload_news = Airtable(base_key, table_name_news, api_key_airtable)
airtable_payload_news = Table(api_key_airtable, base_key, table_name_news)

### DATA UPLOAD FUNCTIONS
#Uploads single json, or list to data_output of record ID as given
def uploadData(inputDictList, recToUpdate):
	recID = recToUpdate
	if isinstance(inputDictList, dict):
		fields = {'output': json.dumps(inputDictList)}
		# fields = {'data_output': str(inputDictList)} #Seems if I do str thats same too
	else:
		fields = {'output': str(inputDictList)}
	airtable_payload_news.update(recID, fields)



#Goes through all records and updates ones that are in the master dict
def updateLoop():
	allRecords = airtable_payload_news.all()
	for i in allRecords:
		try: #In case have a prod payload or anything wrong 
			if "Prod_Ready" in i["fields"]: #Only working on prod ready ie checkboxed
				rec_ofAsked = i["id"]
				data_toUpload = []
				output_native = i["fields"]["output"] #Payload of data asked
				output_json = ast.literal_eval(output_native) #since List from airtable is in String

				for news_item in output_json:
					keywords_ner = []
					keywords_ner_info = []

					article_source = news_item['source_article']

					try:
						news_item['title_article']
						if news_item['title_article'] is not None and news_item['title_article'] != "":
							(keywords, keywords_info) = ner_caller(news_item['title_article'].strip())
							# keywords_ner = keywords_ner + ner_caller(news_item['title_article'].strip())
							keywords_ner = keywords_ner + keywords
							keywords_ner_info = keywords_ner_info + keywords_info
					except NameError:
						continue
					try:
						news_item['content_article']
						if news_item['content_article'] is not None and news_item['content_article'] != "":
							(keywords, keywords_info) = ner_caller(news_item['content_article'].strip())
							# keywords_ner = keywords_ner + ner_caller(news_item['content_article'].strip())
							keywords_ner = keywords_ner + keywords
							keywords_ner_info = keywords_ner_info + keywords_info
					except NameError:
						continue

					if article_source in keywords_ner:
						keywords_ner.remove(article_source)

					keywords_ner = list(set(keywords_ner))

					# At this point, keywords_ner is the source of truth
					# since keywords_ner_info has extra keywords in it.

					news_item['keywords_article'] = keywords_ner
					news_item['keywords_info_article'] = keywords_ner_info
					data_toUpload.append(news_item)

				uploadData(data_toUpload, rec_ofAsked) #Just that bit updated 
				print ("News upload to CMS done..")
		except Exception as e:
			print(e)
	print ("NLP run complete")

updateLoop()

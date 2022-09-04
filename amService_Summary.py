##############
#### ((WIP)) Text Summary NLP -- NOT READY ####
#################
## Summarizes news text and sends back
##############

## WORK ITEMS 
# . What should be installed via requirements.txt?
# . Figure out how the dict structure if happens at task above or here 
#############



import json
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained('facebook/bart-large-cnn')
model = AutoModelForSeq2SeqLM.from_pretrained('facebook/bart-large-cnn')
summarizer = pipeline('summarization', model=model, tokenizer=tokenizer)

# Test 
# print('*'*80)
# print(summarizer)
# print('*'*80)

###### Call Summarization pipeline and get data ######
def summarization_caller(article_in):
	# print(article_in)
	default_summary = summarizer(article_in, truncation=True)
	# long_summary = summarizer(news_item['text_article'], max_length=330, min_length=100, truncation=False)
	# short_summary = summarizer(news_item['text_article'], max_length=50, min_length=10, truncation=False)
	# return {'default_summary': default_summary[0]['summary_text'],
	#         'long_summary': long_summary[0]['summary_text'],
	#         'short_summary': short_summary[0]['summary_text']}
	# return default_summary Original, gives a list
	return default_summary[0]["summary_text"] #Just text
≈
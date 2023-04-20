import pandas as pd
from amService_NLP import ner_caller
from wikiQuery import search_wikidata, wikidata_sparql_get_generic

# # Used to set the User agent string globally for requests
# # This is needed as wikidata2df doesn't set it and for 
# # the number of requests we are sending, wikidata 
# # requires us to set the user agent.
# import requests
# import inspect
# def override_headers(func, global_headers):
#     def wrapper(*args, **kwargs):
#         bound = sig.bind(*args, **kwargs)
#         bound.apply_defaults()
#         bound.arguments.setdefault('headers', {}).update(global_headers)
#         return func(*bound.args, **bound.kwargs)
#     sig = inspect.signature(func)
#     return wrapper
# requests.request = override_headers(func=requests.request, global_headers={'User-Agent': 'User-Agent: automedia/0.0 (https://automedia.ai/; mail@nitinkhanna.com) wikidata2df/1.0'})


samples_file = open('medium_samples.txt', 'r')
Lines = samples_file.readlines()

results_file = open('medium_samples_results.txt', 'a')

augmenter_list = []

for line in Lines:
    augmenter_list.append(line.strip())

while("" in augmenter_list) :
    augmenter_list.remove("")

for sequence_to_augment in augmenter_list:
    print(sequence_to_augment)
    new_sequence = sequence_to_augment
    (keywords, keywords_info) = ner_caller(sequence_to_augment.strip())
    print(keywords, keywords_info)
    if len(keywords) > 0:
        print(keywords, keywords_info)
        for keyword in keywords_info:
            keyword_result = ""

            wd_result = wikidata_sparql_get_generic(keyword['text'], keyword['label'])
            if isinstance(wd_result, pd.DataFrame):
                print("wd_result for debug - ")
                print(wd_result)

                # Exact match is a failure. It's better to make more precise SPARQL
                # queries which sort by relevance.

                print(keyword['text'], wd_result.at[0, 'description'])
                keyword_result = wd_result.at[0, 'description']

                # df_find_exact_match = wd_result.query('itemLabel == "' + keyword['text'] + '"')
                # if df_find_exact_match.empty:
                #     print("No exact match found, going with first result")
                #     print(keyword['text'], wd_result.at[0, 'description'])
                #     keyword_result = wd_result.at[0, 'description']
                # else:
                #     print("Exact match of keyword found, using that to get description")
                #     df_find_exact_match = df_find_exact_match.reset_index(drop=True)
                #     print(keyword['text'], df_find_exact_match.at[0, 'description'])
                #     keyword_result = df_find_exact_match.at[0, 'description']
            else:
                print("**No value found for item:", keyword['text'])

            # if keyword['label'] == 'GPE':
            #     wd_result = wikidata_sparql_get_location(keyword['text'])
            #     if isinstance(wd_result, pd.DataFrame):
            #         print(keyword['text'], wd_result.at[0, 'description'])
            #         keyword_result = wd_result.at[0, 'description']
            #     else:
            #         print("**No value found for ORG:", keyword['text'])
            # elif keyword['label'] == 'ORG':
            #     wd_result = wikidata_sparql_get_org(keyword['text'])
            #     if isinstance(wd_result, pd.DataFrame):
            #         print(keyword['text'], wd_result.at[0, 'description'])
            #         keyword_result = wd_result.at[0, 'description']
            #     else:
            #         print("**No value found for ORG:", keyword['text'])
            # elif keyword['label'] == 'PERSON':
            #     wd_result = wikidata_sparql_get_person(keyword['text'])
            #     if isinstance(wd_result, pd.DataFrame):
            #         print(keyword['text'], wd_result.at[0, 'description'])
            #         keyword_result = wd_result.at[0, 'description']
            #     else:
            #         print("**No value found for PERSON:", keyword['text'])
            # else:
            #     print(keyword['text'], ' - ', search_wikidata(keyword['text']))

            if keyword_result != "":
                new_sequence = new_sequence.replace(keyword['text'], "{} ({})".format(keyword['text'], keyword_result))
    print("new_sequence - ")
    print(new_sequence)

    results_file.write(new_sequence + "\n")
    print('-'*40)

results_file.close()















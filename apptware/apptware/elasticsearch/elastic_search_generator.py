import time


## Create a generator to get all search results
# Get all existing documents from source_index
def es_search_generator(**search_params):
    """Use this to get all results without the need to write the scroll api.
    es_object=es_object_, search_index=search_index_, query_body=query_body_, scroll_time=scroll_time_,
                               page_size=page_size_, doc_type=doc_type_, timeout=timeout_.
    If upto_count = -1, use it till end of results."""

    start_time = time.time()

    es_object = search_params['es_object']
    search_index = search_params['search_index']
    query_body = search_params['query_body']
    scroll_time = search_params['scroll_time']
    page_size = search_params['page_size']
    doc_type = search_params['doc_type']
    timeout = search_params['timeout']
    upto_count = search_params['upto_count']

    response = es_object.search(index=search_index, body=query_body, scroll=scroll_time, size=page_size,
                                doc_type=doc_type, request_timeout=timeout)

    count = 0
    scroll_id = response.get('_scroll_id')  # get initial scroll id
    if scroll_id is None:
        raise StopIteration

    first_run = True
    while True:
        if first_run:
            first_run = False
        else:
            response = es_object.scroll(scroll_id, scroll=scroll_time)
        for hit in response['hits']['hits']:
            if upto_count != -1 and count == upto_count:
                raise StopIteration
            count += 1
            #            if count % 1000 == 0:
            #                print "Time taken to retieve documents from index ", search_index, " at count ", count, " is ", time.time() - start_time

            yield hit

        # Get the new scroll_id
        scroll_id = response.get('_scroll_id')
        if scroll_id is None or not response['hits']['hits']:
            break


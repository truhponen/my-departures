def search_text(input, text):
    result_list = 0
    for item in input:
        if type(input[item]) is dict:
            result_list = result_list + search_text(input[item], text)
        else:
            result_list = result_list + int(text in str(input[item]))
    return result_list

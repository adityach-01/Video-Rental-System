import requests, shutil, json

def save_img(url,filename):
    r = requests.get(url,stream = True)
    if r.status_code == 200:
        with open(filename,'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


url = "https://data-imdb1.p.rapidapi.com/titles/"

querystring = {"info":"base_info"}

headers = {
    "X-RapidAPI-Host": "data-imdb1.p.rapidapi.com",
    "X-RapidAPI-Key": "1bce1e6548msh04953ac9cbfa59ap17fff6jsn63321cf8fe55"
}

link = input("Enter imdb url:")
link = link[link.find('/tt')+1:link.find('/tt')+10]
url = url + link

response = requests.request("GET", url, headers=headers, params=querystring)
response = response.json()['results']
# print(response.json()['results'])

filename = 'movie.json'
file_data = []

with open(filename,mode = 'r+') as file:
    file_data = json.load(file)

    data = {}

    data['id'] = response['id']
    if not isinstance(response['titleText'],type(None)):
        data['title'] = response['titleText']['text']
    else:
        data['title'] = None

    if not isinstance(response['releaseDate'],type(None)):
        data['release_date'] = str(response['releaseDate']['day']) + "-" + str(response['releaseDate']['month']) + "-" + str(response['releaseDate']['year'])
    else:
        data['release_date'] = None

    if not isinstance(response['ratingsSummary'],type(None)):

        if not isinstance(response['ratingsSummary']['aggregateRating'],type(None)):
            data['rating'] = response['ratingsSummary']['aggregateRating']
        else:
            data['rating'] = 0

        if not isinstance(response['ratingsSummary']['voteCount'],type(None)):
            data['votes'] = response['ratingsSummary']['voteCount']
        else:
            data['votes'] = 0
    

    if not isinstance(response['runtime'],type(None)):
        data['runtime'] = response['runtime']['seconds']
    else:
        data['runtime'] = None
    
    if not isinstance(response['runtime'],type(None)):
        data['runtime_sec'] = response['runtime']['seconds']
        hr = data['runtime_sec'] // 3600
        min = (data['runtime_sec'] % 3600) // 60
        data['runtime'] = str(hr) + " hr " + str(min) + " min"
    else:
        data['runtime_sec'] = None
        data['runtime'] = None

    if not isinstance(response['primaryImage'],type(None)):

        data['img_url'] = response['primaryImage']['url']
        data['dim'] = (response['primaryImage']['width'],response['primaryImage']['height'])
        data['img_caption'] = response['primaryImage']['caption']['plainText']
    
    else:
        data['img_url'] = None
        data['dim'] = None
        data['img_caption'] = None

    if not isinstance(response['plot'],type(None)) and not isinstance(response['plot']['plotText'],type(None)):
            data['summary'] = response['plot']['plotText']['plainText']
    else:
        data['summary'] = None

    data['genres'] = []

    if not isinstance(response['genres'],type(None)):
        for gen in response['genres']['genres']:
            data['genres'].append(gen['text'])

    if data['rating'] < 7:
        print(f"Rating of {data['id']} is too low : {data['rating']}")
        exit()
    
    if not isinstance(data['img_url'],type(None)) and not isinstance(data['id'],type(None)):
        filename = "website/static/images/" + str(data['id']) + ".jpg"
        save_img(data['img_url'],filename)
        print(f"Saved image for {data['id']} Successfully.")
    else:
        print(f"No image for {data['id']}")
        exit()

    # file_data.append(data)

    # file.seek(0)
    # json.dump(file_data,file)


from pytube import YouTube
import os
import time
import threading
import validators
import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse

MAX_THREADS=8
API_KEY=""
def downloadAll(links,path):
    result=[]
    i=0
    for link in links:
        t=threading.Thread(target=downloadVideo, args=(link,path,))
        t.start()
        result.append(t)
        i+=1
        if i%MAX_THREADS==0:
            for t in result:
                t.join();
            i=0
            result=[]
    for t in result:
        t.join();


def downloadVideo(link,path):
    yt=YouTube(link)
    video=yt.streams.filter(only_audio=True).first()
    outputfile=video.download(output_path=path)
    base,ext=os.path.splitext(outputfile)
    newfile=base+".mp3"
    os.rename(outputfile,newfile)
    print("["+yt.title+"] Has been SUCCESSFULLY downloaded!")

def start():
    while(True):
        c=choice()
        if(c==0):
            filename,path=fileinputs()
            text_file = open(filename, "r")
            lines = text_file.readlines()
            start_time = time.perf_counter()
            downloadAll(lines,path)
            end_time = time.perf_counter()
        elif(c==1):
            t=checkApiKey()
            if(t==False):
                continue
            url,path=playlistinputs()
            links=generateLinesFromPlaylist(url)
            start_time = time.perf_counter()
            downloadAll(links,path)
            end_time = time.perf_counter()
        else:
            str(input("Press any key to exit"))
            return
        print("Success! all files saved to "+path)
        print(f'Task Finished in {end_time- start_time: 0.2f}s')
        str(input("Press any key to Continue."))

def checkApiKey():
    if(API_KEY==""):
        print("It seems you do not have an API KEY. in case you had one set your API_KEY variable!")
        return False
    return True
        
def generateLinesFromPlaylist(url):
    result=[]
    #extract playlist id from url
    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    playlist_id = query["list"][0]
    print(f'getting all playlist items links from {playlist_id}')
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = API_KEY)
    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = playlist_id,
        maxResults = 50
    )
    response = request.execute()
    playlist_items = []
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)
    print(f"total: {len(playlist_items)}")
    for t in playlist_items:
        result.append(f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}&list={playlist_id}&t=0s')
    return result

def choice():
    print("INPUT 0 TO DOWNLOAD A LINK FILE")
    print("INPUT 1 TO DOWNLOAD A PLAYLIST (needs Google API key v3)")
    print("INPUT -1 TO EXIT PROGRAM")
    ch=int(input(">>"))
    return ch

def fileinputs():
    ok=False
    while(ok==False):
        filename=str(input("Youtube Links file (one link per row!)>> "))
        path=str(input("Enter the destination (leave blank for current directory)>> "))
        isok=str(input("Are filename and path correct? (yes/no)"))
        if(path==""):
                    path="."
        if(isok=="yes" or isok=="y"):
                    if(os.path.exists(filename)==False):
                        print("youtube links file does not exist/invalid!")
                    elif(os.path.exists(path)==False):
                        print("Destination folder does not exist/invalid!")
                    else:
                        ok=True
    return filename,path

def playlistinputs():
    ok=False
    while(ok==False):
        link=str(input("Youtube playlist link>> "))
        path=str(input("Enter the destination (leave blank for current directory)>> "))
        isok=str(input("Are playlist link and path correct? (yes/no)"))
        if(path==""):
                    path="."
        if(isok=="yes" or isok=="y"):
                    if(validators.url(link)==False):
                        print("youtube links file does not exist/invalid!")
                    elif(os.path.exists(path)==False):
                        print("Destination folder does not exist/invalid!")
                    else:
                        ok=True
    return link,path
if __name__ == "__main__":
    start();

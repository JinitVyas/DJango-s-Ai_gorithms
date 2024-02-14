from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .process_functions import Call
import json
from django.http import JsonResponse

# Create your views here.
def index(request):
    return render(request, "index.html")
    # return HttpResponse("This is homepage")

def run_get_token(request):
    request.session['api__token'] = Call.get_token()
    return HttpResponseRedirect("/")

def run_get_song_details(request):
    query = request.POST.get('q')
    token = request.POST.get('token')
    track = Call.get_song_details(query, token)
    
    # return render(request, "index.html")
    return JsonResponse(track)

def run_get_recommendation(request):
    seed_track = request.POST.get('track_id')
    seed_artist = request.POST.get('artist_id')
    token = request.session['api__token']
    result_recommendation = Call.get_recommendation(limit=50, seed_track=seed_track, seed_artist=seed_artist,token=token )

    return JsonResponse(result_recommendation)

def run_get_features(request):
    track_id = request.POST.get('track_id')
    access_token = request.session.get('api__token')
    # print("*******************************************", track_id, " ", access_token)
    result = Call.get_features(track_id=track_id, access_token=access_token)
    # print(result)
    return JsonResponse(result)

def run_get_top10(request):
    if request.method == 'POST' and 'f1' in request.POST:
        TargetInfo = request.POST.get('f1')
        TargetFeatures = request.POST.get('f2')
        RecommendedInfo = request.POST.get('f3')
        RecommendedFeatures = request.POST.get('f4')
        if TargetInfo:
            try:
                f1 = json.loads(RecommendedInfo)
                # print(f1)
                top_10_ids = Call.get_top10(targetFeatures=TargetFeatures,target_track=TargetInfo,_100Features=RecommendedFeatures,_100Tracks=RecommendedInfo).tolist()

                return JsonResponse({"message": "Data received successfully", "top10": top_10_ids})
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data in 'f1'"}, status=400)
        else:
            return JsonResponse({"error": "'f1' parameter is empty"}, status=400)
    else:
        return JsonResponse({"error": "POST request with 'f1' parameter required"}, status=400)



def end(request):
    request.session.clear()
    return render(request,"index.html")
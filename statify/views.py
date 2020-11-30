"""
@file           views.py
@author         Max Legrand
@description    Process data for display
@lastUpdated    11/18/2020
"""

from collections import Counter
from django.shortcuts import render, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from . import models
import re

import json

CONFIG_FILE = open("config.json")
CONFIG = json.load(CONFIG_FILE)
CONFIG_FILE.close()

scope = "user-library-read user-read-recently-played user-top-read"

auth = SpotifyOAuth(
        scope=scope,
        client_id=CONFIG["clientid"],
        client_secret=CONFIG["clientsecret"],
        redirect_uri="",
)


def mobile(request):
    """
    check if request is coming from mobile device

    Args:
        request (HttpRequest): request object

    Returns:
        boolean: True if mobile, False otherwise
    """
    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False


def home(request):
    """
    Function to render home page

    Args:
        request (HttpRequest): request object

    Returns:
        HttpResponse: render of home page
    """
    if "id" in request.session:
        res = request.session["id"]
    else:
        res = None
    return render(request, "statify/view.html", {"res": res, "is_mobile": mobile(request)})


def loginspotify(request):
    return redirect(auth.get_authorize_url())


def logoutspotify(request):
    token = models.Auth.objects.all().filter(id=request.session["id"])[0]
    token.delete()
    del request.session['id']
    return redirect("/")


def authorize(request):
    token = auth.get_access_token(code=request.GET["code"], check_cache=False, as_dict=True)
    sp = spotipy.Spotify(auth_manager=auth) # noqa
    newuser = models.Auth(token=token)
    newuser.save()
    request.session["id"] = newuser.id
    return redirect("/")


def top_tracks(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        current = sp.current_user_top_tracks(limit=20, time_range="short_term")
        recent_tracks = []
        tracks = current["items"]
        images = []
        weblinks = []
        applinks = []

        for track in tracks:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["external_urls"]["spotify"])
                applinks.append(track["uri"])
                images.append(track["album"]["images"][0]["url"])
                recent_tracks.append(final)

        current = sp.current_user_top_tracks(limit=20, offset=20, time_range="short_term")
        tracks = current["items"]
        for track in tracks:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["external_urls"]["spotify"])
                applinks.append(track["uri"])
                images.append(track["album"]["images"][0]["url"])
                recent_tracks.append(final)

        current = sp.current_user_top_tracks(limit=20, offset=40, time_range="short_term")
        tracks = current["items"]
        for track in tracks:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["external_urls"]["spotify"])
                applinks.append(track["uri"])
                images.append(track["album"]["images"][0]["url"])
                recent_tracks.append(final)

        if mobile(request):
            is_mobile = True
            results = zip(recent_tracks, images, weblinks, applinks)
        else:
            is_mobile = False
            recent_tracks1, recent_tracks2, recent_tracks3 = split_array(recent_tracks)
            images1, images2, images3 = split_array(images)
            weblinks1, weblinks2, weblinks3 = split_array(weblinks)
            applinks1, applinks2, applinks3 = split_array(applinks)
            results = zip(
                recent_tracks1, images1, weblinks1, applinks1,
                recent_tracks2, images2, weblinks2, applinks2,
                recent_tracks3, images3, weblinks3, applinks3
            )
        return render(request, "statify/top_tracks.html", {"tracks": results, "mobile": is_mobile})
    else:
        return redirect("/")


def split_array(list):
    list1 = []
    list2 = []
    list3 = []
    for counter in range(0, len(list), 6):
        list1.append(list[counter])
        try:
            list2.append(list[counter+1])
        except: # noqa
            list2.append(None)
        try:
            list3.append(list[counter+2])
        except: # noqa
            list3.append(None)
        try:
            list1.append(list[counter+3])
        except: # noqa
            list1.append(None)
        try:
            list2.append(list[counter+4])
        except: # noqa
            list2.append(None)
        try:
            list3.append(list[counter+5])
        except: # noqa
            list3.append(None)
    return list1, list2, list3


def recent_genres(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        current = sp.current_user_recently_played(limit=50)
        genres = Counter()
        seen_tracks = []

        tracks = current["items"]
        for track in tracks:
            if track["track"]["name"] not in seen_tracks:
                for artist in track["track"]["artists"]:
                    info = sp.artist(artist["id"])
                    for genre in info["genres"]:
                        genres[genre] += 1
                seen_tracks.append(track["track"]["name"])
        genres = genres.most_common(10)
        labels = []
        values = []
        for genre in genres:
            labels.append(genre[0])
            values.append(genre[1])
        return render(
            request,
            "statify/recent_genres.html",
            {"labels": labels, "datas": values, "ismobile": mobile(request)}
        )

    else:
        return redirect("/")


def recent_tracks(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        current = sp.current_user_recently_played(limit=50)
        recent_tracks = []
        tracks = current["items"]
        images = []
        weblinks = []
        applinks = []
        for track in tracks:
            name = track["track"]["name"]
            artists = []
            for artist in track["track"]["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["track"]["external_urls"]["spotify"])
                applinks.append(track["track"]["uri"])
                images.append(track["track"]["album"]["images"][0]["url"])
                recent_tracks.append(final)

        if mobile(request):
            is_mobile = True
            results = zip(recent_tracks, images, weblinks, applinks)
        else:
            is_mobile = False
            recent_tracks1, recent_tracks2, recent_tracks3 = split_array(recent_tracks)
            images1, images2, images3 = split_array(images)
            weblinks1, weblinks2, weblinks3 = split_array(weblinks)
            applinks1, applinks2, applinks3 = split_array(applinks)
            results = zip(
                recent_tracks1, images1, weblinks1, applinks1,
                recent_tracks2, images2, weblinks2, applinks2,
                recent_tracks3, images3, weblinks3, applinks3
            )
        return render(request, "statify/recent_tracks.html", {"tracks": results, "mobile": is_mobile})
    else:
        return redirect("/")


def recent_artists(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        current = sp.current_user_recently_played(limit=50)

        names = []
        images = []
        weblinks = []
        applinks = []
        popularity = []
        tracks = current["items"]
        for track in tracks:
            for artist in track["track"]["artists"]:
                if artist["name"] not in names:
                    info = sp.artist(artist["id"])
                    names.append(artist["name"])
                    try:
                        images.append(info["images"][0]["url"])
                    except: # noqa
                        images.append(None)
                    weblinks.append(info["external_urls"]["spotify"])
                    applinks.append(info["uri"])
                    popularity.append(info["popularity"])

        if mobile(request):
            is_mobile = True
            results = zip(names, images, weblinks, applinks, popularity)
        else:
            is_mobile = False
            names1, names2, names3 = split_array(names)
            images1, images2, images3 = split_array(images)
            weblinks1, weblinks2, weblinks3 = split_array(weblinks)
            applinks1, applinks2, applinks3 = split_array(applinks)
            popularity1, popularity2, popularity3 = split_array(popularity)
            results = zip(
                names1, images1, weblinks1, applinks1, popularity1,
                names2, images2, weblinks2, applinks2, popularity2,
                names3, images3, weblinks3, applinks3, popularity3
            )

        return render(request, "statify/recent_artists.html", {"infos": results, "mobile": is_mobile})
    else:
        return redirect("/")


def top_tracks_med(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        current = sp.current_user_top_tracks(limit=20, time_range="medium_term")
        recent_tracks = []
        tracks = current["items"]
        images = []
        weblinks = []
        applinks = []

        for track in tracks:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["external_urls"]["spotify"])
                applinks.append(track["uri"])
                images.append(track["album"]["images"][0]["url"])
                recent_tracks.append(final)

        current = sp.current_user_top_tracks(limit=20, offset=20, time_range="medium_term")
        tracks = current["items"]
        for track in tracks:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["external_urls"]["spotify"])
                applinks.append(track["uri"])
                images.append(track["album"]["images"][0]["url"])
                recent_tracks.append(final)

        current = sp.current_user_top_tracks(limit=20, offset=40, time_range="medium_term")
        tracks = current["items"]
        for track in tracks:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["external_urls"]["spotify"])
                applinks.append(track["uri"])
                images.append(track["album"]["images"][0]["url"])
                recent_tracks.append(final)

        if mobile(request):
            is_mobile = True
            results = zip(recent_tracks, images, weblinks, applinks)
        else:
            is_mobile = False
            recent_tracks1, recent_tracks2, recent_tracks3 = split_array(recent_tracks)
            images1, images2, images3 = split_array(images)
            weblinks1, weblinks2, weblinks3 = split_array(weblinks)
            applinks1, applinks2, applinks3 = split_array(applinks)
            results = zip(
                recent_tracks1, images1, weblinks1, applinks1,
                recent_tracks2, images2, weblinks2, applinks2,
                recent_tracks3, images3, weblinks3, applinks3
            )
        return render(request, "statify/top_tracks_med.html", {"tracks": results, "mobile": is_mobile})
    else:
        return redirect("/")


def top_tracks_long(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        current = sp.current_user_top_tracks(limit=20, time_range="long_term")
        recent_tracks = []
        tracks = current["items"]
        images = []
        weblinks = []
        applinks = []

        for track in tracks:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["external_urls"]["spotify"])
                applinks.append(track["uri"])
                images.append(track["album"]["images"][0]["url"])
                recent_tracks.append(final)

        current = sp.current_user_top_tracks(limit=20, offset=20, time_range="long_term")
        tracks = current["items"]
        for track in tracks:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["external_urls"]["spotify"])
                applinks.append(track["uri"])
                images.append(track["album"]["images"][0]["url"])
                recent_tracks.append(final)

        current = sp.current_user_top_tracks(limit=20, offset=40, time_range="long_term")
        tracks = current["items"]
        for track in tracks:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            final = name + " – "
            start = True
            for item in artists:
                if start:
                    final += item
                    start = False
                else:
                    final += ", " + item
            if final not in recent_tracks:
                weblinks.append(track["external_urls"]["spotify"])
                applinks.append(track["uri"])
                images.append(track["album"]["images"][0]["url"])
                recent_tracks.append(final)

        if mobile(request):
            is_mobile = True
            results = zip(recent_tracks, images, weblinks, applinks)
        else:
            is_mobile = False
            recent_tracks1, recent_tracks2, recent_tracks3 = split_array(recent_tracks)
            images1, images2, images3 = split_array(images)
            weblinks1, weblinks2, weblinks3 = split_array(weblinks)
            applinks1, applinks2, applinks3 = split_array(applinks)
            results = zip(
                recent_tracks1, images1, weblinks1, applinks1,
                recent_tracks2, images2, weblinks2, applinks2,
                recent_tracks3, images3, weblinks3, applinks3
            )
        return render(request, "statify/top_tracks_long.html", {"tracks": results, "mobile": is_mobile})
    else:
        return redirect("/")


def top_artists(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        current = sp.current_user_top_artists(limit=20, time_range="short_term")

        names = []
        images = []
        weblinks = []
        applinks = []
        popularity = []
        artists = current["items"]
        for artist in artists:
            names.append(artist["name"])
            try:
                images.append(artist["images"][0]["url"])
            except: # noqa
                images.append(None)
            weblinks.append(artist["external_urls"]["spotify"])
            applinks.append(artist["uri"])
            popularity.append(artist["popularity"])

        current = sp.current_user_top_artists(limit=20, offset=20, time_range="short_term")
        artists = current["items"]
        for artist in artists:
            names.append(artist["name"])
            try:
                images.append(artist["images"][0]["url"])
            except: # noqa
                images.append(None)
            weblinks.append(artist["external_urls"]["spotify"])
            applinks.append(artist["uri"])
            popularity.append(artist["popularity"])

        current = sp.current_user_top_artists(limit=20, offset=40, time_range="short_term")
        artists = current["items"]
        for artist in artists:
            names.append(artist["name"])
            try:
                images.append(artist["images"][0]["url"])
            except: # noqa
                images.append(None)
            weblinks.append(artist["external_urls"]["spotify"])
            applinks.append(artist["uri"])
            popularity.append(artist["popularity"])

        if mobile(request):
            is_mobile = True
            results = zip(names, images, weblinks, applinks, popularity)
        else:
            is_mobile = False
            names1, names2, names3 = split_array(names)
            images1, images2, images3 = split_array(images)
            weblinks1, weblinks2, weblinks3 = split_array(weblinks)
            applinks1, applinks2, applinks3 = split_array(applinks)
            popularity1, popularity2, popularity3 = split_array(popularity)
            results = zip(
                names1, images1, weblinks1, applinks1, popularity1,
                names2, images2, weblinks2, applinks2, popularity2,
                names3, images3, weblinks3, applinks3, popularity3
            )

        return render(request, "statify/top_artists.html", {"infos": results, "mobile": is_mobile})
    else:
        return redirect("/")


def top_artists_med(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        current = sp.current_user_top_artists(limit=20, time_range="medium_term")

        names = []
        images = []
        weblinks = []
        applinks = []
        popularity = []
        artists = current["items"]
        for artist in artists:
            names.append(artist["name"])
            try:
                images.append(artist["images"][0]["url"])
            except: # noqa
                images.append(None)
            weblinks.append(artist["external_urls"]["spotify"])
            applinks.append(artist["uri"])
            popularity.append(artist["popularity"])

        current = sp.current_user_top_artists(limit=20, offset=20, time_range="medium_term")
        artists = current["items"]
        for artist in artists:
            names.append(artist["name"])
            try:
                images.append(artist["images"][0]["url"])
            except: # noqa
                images.append(None)
            weblinks.append(artist["external_urls"]["spotify"])
            applinks.append(artist["uri"])
            popularity.append(artist["popularity"])

        current = sp.current_user_top_artists(limit=20, offset=40, time_range="medium_term")
        artists = current["items"]
        for artist in artists:
            names.append(artist["name"])
            try:
                images.append(artist["images"][0]["url"])
            except: # noqa
                images.append(None)
            weblinks.append(artist["external_urls"]["spotify"])
            applinks.append(artist["uri"])
            popularity.append(artist["popularity"])

        if mobile(request):
            is_mobile = True
            results = zip(names, images, weblinks, applinks, popularity)
        else:
            is_mobile = False
            names1, names2, names3 = split_array(names)
            images1, images2, images3 = split_array(images)
            weblinks1, weblinks2, weblinks3 = split_array(weblinks)
            applinks1, applinks2, applinks3 = split_array(applinks)
            popularity1, popularity2, popularity3 = split_array(popularity)
            results = zip(
                names1, images1, weblinks1, applinks1, popularity1,
                names2, images2, weblinks2, applinks2, popularity2,
                names3, images3, weblinks3, applinks3, popularity3
            )

        return render(request, "statify/top_artists_med.html", {"infos": results, "mobile": is_mobile})
    else:
        return redirect("/")


def top_artists_long(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        current = sp.current_user_top_artists(limit=20, time_range="long_term")

        names = []
        images = []
        weblinks = []
        applinks = []
        popularity = []
        artists = current["items"]
        for artist in artists:
            names.append(artist["name"])
            try:
                images.append(artist["images"][0]["url"])
            except: # noqa
                images.append(None)
            weblinks.append(artist["external_urls"]["spotify"])
            applinks.append(artist["uri"])
            popularity.append(artist["popularity"])

        current = sp.current_user_top_artists(limit=20, offset=20, time_range="long_term")
        artists = current["items"]
        for artist in artists:
            names.append(artist["name"])
            try:
                images.append(artist["images"][0]["url"])
            except: # noqa
                images.append(None)
            weblinks.append(artist["external_urls"]["spotify"])
            applinks.append(artist["uri"])
            popularity.append(artist["popularity"])

        current = sp.current_user_top_artists(limit=20, offset=40, time_range="long_term")
        artists = current["items"]
        for artist in artists:
            names.append(artist["name"])
            try:
                images.append(artist["images"][0]["url"])
            except: # noqa
                images.append(None)
            weblinks.append(artist["external_urls"]["spotify"])
            applinks.append(artist["uri"])
            popularity.append(artist["popularity"])

        if mobile(request):
            is_mobile = True
            results = zip(names, images, weblinks, applinks, popularity)
        else:
            is_mobile = False
            names1, names2, names3 = split_array(names)
            images1, images2, images3 = split_array(images)
            weblinks1, weblinks2, weblinks3 = split_array(weblinks)
            applinks1, applinks2, applinks3 = split_array(applinks)
            popularity1, popularity2, popularity3 = split_array(popularity)
            results = zip(
                names1, images1, weblinks1, applinks1, popularity1,
                names2, images2, weblinks2, applinks2, popularity2,
                names3, images3, weblinks3, applinks3, popularity3
            )

        return render(request, "statify/top_artists_long.html", {"infos": results, "mobile": is_mobile})
    else:
        return redirect("/")


def top_genres(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        genres = Counter()

        current = sp.current_user_top_artists(limit=20, time_range="short_term")
        artists = current["items"]
        for artist in artists:
            for genre in artist["genres"]:
                genres[genre] += 1

        current = sp.current_user_top_artists(limit=20, offset=20, time_range="short_term")
        artists = current["items"]
        for artist in artists:
            for genre in artist["genres"]:
                genres[genre] += 1

        current = sp.current_user_top_artists(limit=20, offset=40, time_range="short_term")
        artists = current["items"]
        for artist in artists:
            for genre in artist["genres"]:
                genres[genre] += 1

        genres = genres.most_common(10)
        labels = []
        values = []
        for genre in genres:
            labels.append(genre[0])
            values.append(genre[1])
        return render(
            request,
            "statify/top_genres.html",
            {"labels": labels, "datas": values, "ismobile": mobile(request)}
        )

    else:
        return redirect("/")


def top_genres_med(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        genres = Counter()

        current = sp.current_user_top_artists(limit=20, time_range="medium_term")
        artists = current["items"]
        for artist in artists:
            for genre in artist["genres"]:
                genres[genre] += 1

        current = sp.current_user_top_artists(limit=20, offset=20, time_range="medium_term")
        artists = current["items"]
        for artist in artists:
            for genre in artist["genres"]:
                genres[genre] += 1

        current = sp.current_user_top_artists(limit=20, offset=40, time_range="medium_term")
        artists = current["items"]
        for artist in artists:
            for genre in artist["genres"]:
                genres[genre] += 1

        genres = genres.most_common(10)
        labels = []
        values = []
        for genre in genres:
            labels.append(genre[0])
            values.append(genre[1])
        return render(
            request,
            "statify/top_genres_med.html",
            {"labels": labels, "datas": values, "ismobile": mobile(request)}
        )

    else:
        return redirect("/")


def top_genres_long(request):
    if "id" in request.session:
        token = models.Auth.objects.all().filter(id=request.session["id"])[0]
        auth._save_token_info(token.token)
        sp = spotipy.Spotify(auth_manager=auth)
        genres = Counter()

        current = sp.current_user_top_artists(limit=20, time_range="long_term")
        artists = current["items"]
        for artist in artists:
            for genre in artist["genres"]:
                genres[genre] += 1

        current = sp.current_user_top_artists(limit=20, offset=20, time_range="long_term")
        artists = current["items"]
        for artist in artists:
            for genre in artist["genres"]:
                genres[genre] += 1

        current = sp.current_user_top_artists(limit=20, offset=40, time_range="long_term")
        artists = current["items"]
        for artist in artists:
            for genre in artist["genres"]:
                genres[genre] += 1

        genres = genres.most_common(10)
        labels = []
        values = []
        for genre in genres:
            labels.append(genre[0])
            values.append(genre[1])
        return render(
            request,
            "statify/top_genres_long.html",
            {"labels": labels, "datas": values, "ismobile": mobile(request)}
        )

    else:
        return redirect("/")


def about(request):
    if "id" in request.session:
        res = request.session["id"]
    else:
        res = None
    return render(request, "statify/about.html", {"res": res, "is_mobile": mobile(request)})

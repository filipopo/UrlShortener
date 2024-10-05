import json
from django import forms
from .models import ShortUrl
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_safe, require_POST


class UrlForm(forms.Form):
    url = forms.URLField(max_length=255)
    path = forms.CharField(required=False, max_length=255)
    note = forms.CharField(required=False, max_length=255)


# 73 characters, 62 alpha-numeric
convertor = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$-_.+!*'(),"


def encode(num):
    if (num >= len(convertor)):
        res = encode(num // len(convertor))
    else:
        res = ''

    res += convertor[num % len(convertor)]
    return res


def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    elif request.method == 'POST':
        res = json.loads(urls(request).content)
        return render(request, 'index.html', {'res': res})


@require_safe
def u(request, path):
    res = json.loads(url(request, path).content)
    if res['url']:
        if res['note']:
            return render(request, 'note.html', {'res': res})

        return redirect(res['url'])
    raise Http404


@require_safe
def url(request, path):
    try:
        res = ShortUrl.objects.get(short=path)
    except ShortUrl.DoesNotExist:
        return JsonResponse({'url': False})
    # except ShortUrl.MultipleObjectsReturned:

    res.viewed += 1
    res.save()

    return JsonResponse({
        'url': res.url,
        'note': res.note
    })


@require_POST
def urls(request):
    form = UrlForm(request.POST)
    if form.is_valid():
        num = ShortUrl.objects.latest().id if ShortUrl.objects.exists() else 0
        short = form.cleaned_data['path']

        if short:
            if ShortUrl.objects.filter(short=short):
                return JsonResponse({
                    'message': 'This url is already taken',
                    'url': False
                })
        else:
            short = encode(num)
            while ShortUrl.objects.filter(short=short):
                num += 1
                short = encode(num)

        short = ShortUrl(
            id=num + 1,
            short=short,
            url=form.cleaned_data['url'],
            note=form.cleaned_data['note']
        )

        short.save()
        return JsonResponse({
            'message': f'{request.scheme}://{request.get_host()}/u/{short.short}',
            'url': True
        })

    return JsonResponse({
        'message': json.dumps(form.errors)[1:-1],  # Removes the "{}"
        'url': False
    })

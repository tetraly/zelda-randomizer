import base64
import binascii
import hashlib
import json
import random

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView

from .models import Seed, Patch
from .forms import GenerateForm, FLAGS
from .randomizer.patch import PatchJSONEncoder
from .randomizer.randomizer import Z1Randomizer, VERSION
from .randomizer.settings import Settings


class RandomizerView(TemplateView):
    """
    Base class for views that generate a ROM, i.e. randomizer and patch-from-hash views.
    This gets common context data.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['version'] = VERSION
        context['debug_enabled'] = settings.DEBUG
        context['flags'] = FLAGS
        return context


class AboutView(RandomizerView):
    template_name = 'randomizer/about.html'


class HowToPlayView(RandomizerView):
    template_name = 'randomizer/how_to_play.html'


class OptionsView(RandomizerView):
    template_name = 'randomizer/options.html'


class ResourcesView(RandomizerView):
    template_name = 'randomizer/resources.html'


class UpdatesView(RandomizerView):
    template_name = 'randomizer/updates.html'


class RandomizeView(RandomizerView):
    template_name = 'randomizer/randomize.html'


class HashView(RandomizerView):
    template_name = 'randomizer/patch_from_hash.html'

class GenerateView(FormView):
    form_class = GenerateForm

    def form_valid(self, form):
        data = form.cleaned_data

        # Debug mode is only allowed if the server is running in debug mode for development.
        if not settings.DEBUG:
            data['debug_mode'] = False

        # If seed is provided, use it.  Otherwise generate a random seed (10 digits max).
        # For non-numeric values, take the CRC32 checksum of it.
        seed = data['seed']
        if seed:
            if seed.isdigit():
                seed = int(seed)
                if seed < 1:
                    seed = None
            else:
                seed = binascii.crc32(seed.encode())

        # If seed is not provided, generate a 32 bit seed integer using the CSPRNG.
        if not seed:
            r = random.SystemRandom()
            seed = r.getrandbits(32)
            del r

        mode = data['mode']
        debug_mode = data['debug_mode']

        # Compute hash based on seed and selected options.  Use first 10 characters for convenience.
        h = hashlib.md5()
        h.update(VERSION.encode('utf-8'))
        h.update(seed.to_bytes(4, 'big'))
        h.update(mode.encode('utf-8'))
        h.update(str(debug_mode).encode('utf-8'))
        if mode == 'custom':
            for flag in FLAGS:
                h.update(str(data[flag[0]]).encode('utf-8'))

        hash = base64.b64encode(h.digest()).decode().replace('+', '').replace('/', '')[:10]

        # Get custom flags.
        custom_flags = {}
        for flag in FLAGS:
            custom_flags[flag[0]] = data[flag[0]]

        randomizer = Z1Randomizer()
        randomizer.ConfigureSettings(seed, Settings(mode, debug_mode, custom_flags))

        patches = {'US': randomizer.GetPatch()}

        # Send back patch data.
        result = {
            'logic': VERSION,
            'seed': seed,
            'hash': hash,
            'mode': mode,
            'debug_mode': debug_mode,
            'custom_flags': custom_flags,
        }

        result['patch'] = patches['US']  # Patch for EU version is the same as US.
        return JsonResponse(result, encoder=PatchJSONEncoder)

    def form_invalid(self, form):
        msg = "ERRORS: " + '; '.join(form.errors)
        return HttpResponseBadRequest(msg.encode())


class GenerateFromHashView(View):
    def get(self, request, hash):
        """Get a previously generated patch via hash value."""

        try:
            s = Seed.objects.get(hash=hash)
        except Seed.DoesNotExist:
            return HttpResponseNotFound("No record for hash {0!r}".format(hash))

        try:
            p = Patch.objects.get(seed=s, region=region)
        except Patch.DoesNotExist:
            return HttpResponseNotFound("No patch found for hash {0!r}, region {1!r}".format(hash, region))

        result = {
            'logic': s.version,
            'seed': s.seed,
            'hash': s.hash,
            'mode': s.mode,
            'debug_mode': s.debug_mode,
            'custom_flags': json.loads(s.flags),
            'patch': json.loads(p.patch),
        }
        return JsonResponse(result)

import base64
import binascii
import hashlib
import json
import os
import random
import string
import tempfile
import shutil

import Wii
import nlzss

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

        # Build game world, randomize it, and generate the patch.
        #        world = GameWorld(seed, Settings(mode, debug_mode, custom_flags))
        #        world.randomize()
        randomizer = Z1Randomizer()
        randomizer.ConfigureSettings(Settings(mode, debug_mode, custom_flags))
        #randomizer.SetFlags(
        #     input_filename="This doesn't matter",
        #     output_location="This also doesn't matter",
        #     seed=seed,
        #     text_speed="normal",
        #     level_text="hello-")

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

        #if data['region'] == 'EU':
        result['patch'] = patches['US']  # Patch for EU version is the same as US.
        #else:
        #    result['patch'] = patches[data['region']]
        return JsonResponse(result, encoder=PatchJSONEncoder)

    def form_invalid(self, form):
        msg = "ERRORS: " + '; '.join(form.errors)
        return HttpResponseBadRequest(msg.encode())


class GenerateFromHashView(View):
    def get(self, request, hash, region):
        """Get a previously generated patch via hash value."""

        # EU patch is actually the US one.
        if region == 'EU':
            region = 'US'

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


@method_decorator(csrf_exempt, name='dispatch')
class PackingView(View):
    def post(self, request):
        """Pack uploaded ROM into the provided WAD file as downloaded file."""
        if not request.FILES.get('rom'):
            return HttpResponseBadRequest("ROM file not provided")
        elif not request.FILES.get('wad'):
            return HttpResponseBadRequest("WAD file not provided")

        with tempfile.TemporaryDirectory() as dumpdir:
            romfile = os.path.join(dumpdir, 'rom.sfc')
            with open(romfile, 'wb') as f:
                shutil.copyfileobj(request.FILES['rom'], f)

            # Compress ROM file for US and EU (not JP)
            rom_to_copy = romfile
            if request.POST.get('region') in ('US', 'EU'):
              romcompressed = os.path.join(dumpdir, 'rom_compressed.sfc')
              nlzss.encode_file(romfile, romcompressed)
              rom_to_copy = romcompressed

            # Dump WAD file
            wadf = Wii.WAD.load(request.FILES['wad'].read())
            wadf.dumpDir(dumpdir)

            # Dump U8 archive
            u8file = os.path.join(dumpdir, '00000005.app')
            u8unpackdir = u8file + '_unpacked'
            u8archive = Wii.U8.loadFile(u8file)
            u8archive.dumpDir(u8unpackdir)

            # Copy randomized ROM over
            for f in os.listdir(u8unpackdir):
                if f.lower().endswith(".rom"):
                    wadrom = os.path.join(u8unpackdir, f)
                    shutil.copyfile(rom_to_copy, wadrom)
                    break

            # Put U8 archive back together
            newu8 = Wii.U8.loadDir(u8unpackdir)
            newu8.dumpFile(u8file)

            # Build new WAD
            newwadfile = os.path.join(dumpdir, 'smrpg_randomized.wad')
            newwad = Wii.WAD.loadDir(dumpdir)

            # Make new channel title with seed (sync for all languages).
            # Read title from ROM and make sure it's in the correct spot.  If not, leave the title alone.
            with open(romfile, 'rb') as f:
                f.seek(0x7fc0)
                title = f.read(20).strip()
                title = title.ljust(20)

            if not title.startswith(b'SMRPG-R'):
                return HttpResponseBadRequest("Bad ROM title {!r}".format(title))

            try:
                seed = int(title[7:].strip())
            except:
                return HttpResponseBadRequest("Bad ROM title {!r}".format(title))

            # Read first content file data to find the channel title data and update it.
            if newwad.contents[0][0x80:0x84] != b'IMET':
                return HttpResponseBadRequest("Can't find IMET in WAD contents file")

            imetpos = 0x80
            i = 0
            content = bytearray(newwad.contents[0])

            # Channel names start 29 bytes after the "IMET" string, and there are 7 of them in a row.
            jpos = imetpos + 29
            for i in list(range(7)):
                for j, char in enumerate(title):
                    pos = jpos + (i * 84) + (j * 2)
                    content[pos] = char

            # Update MD5 hash for this content file.
            data = content[64:1584]
            data += b'\x00' * 16
            hash = Wii.Crypto.createMD5Hash(data)
            for i in range(16):
                content[1584 + i] = hash[i]

            newwad.contents[0] = bytes(content)

            # Generate random title ID for the WAD that doesn't conflict with existing channels.
            choices = list(string.ascii_letters + string.digits)
            # The first character of the four byte title ID should exclude existing ones to avoid conflicts.
            first_char_choices = list(set(choices) -
                                      {'C', 'D', 'E', 'F', 'G', 'H', 'J', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'W', 'X'})
            first_char_choices.sort()

            random.seed(seed)
            new_id = bytearray([0x00, 0x01, 0x00, 0x01, ord(random.choice(first_char_choices))])
            for i in range(3):
                new_id.append(ord(random.choice(choices)))

            tid = int.from_bytes(new_id, 'big')
            newwad.tmd.setTitleID(tid)
            newwad.tik.setTitleID(tid)

            newwad.dumpFile(newwadfile, fakesign=False)

            # Return new WAD file
            response = HttpResponse(open(newwadfile, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="smrpg.wad"'
            return response

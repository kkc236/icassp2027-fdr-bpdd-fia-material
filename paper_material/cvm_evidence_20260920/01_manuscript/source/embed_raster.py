"""Lossless RGB XObjects embedded as ASCII for single-file pdfLaTeX."""
from pathlib import Path
from PIL import Image
import zlib,textwrap

def raster_xobject(name,path):
    im=Image.open(path).convert('RGB')
    w,h=im.size
    compressed=zlib.compress(im.tobytes(),9).hex().upper()+'>'
    lines='\n'.join(textwrap.wrap(compressed,120))
    tex=(r'\begingroup\pdfcompresslevel=0'+'\n'+
         r'\immediate\pdfobj stream attr{ /Type /XObject /Subtype /Image '+
         f'/Width {w} /Height {h} '+
         r'/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter [/ASCIIHexDecode /FlateDecode] }{'+
         '\n'+lines+'\n}\n'+
         r'\expandafter\xdef\csname imageobj'+name+r'\endcsname{\the\pdflastobj}'+'\n'+r'\endgroup'+'\n')
    return tex, f'/{name} '+r'\csname imageobj'+name+r'\endcsname'+r'\space 0 R', h/w

def embed_assets(assets):
    streams=[]; resources=[]; commands=[]
    for name,path in assets.items():
        code,resource,ratio=raster_xobject(name,path)
        streams.append(code); resources.append(resource)
        commands.append(r'\expandafter\newcommand\csname visual'+name+r'\endcsname[1]{\begingroup'+
                        r'\dimen0=#1\relax\dimen2='+f'{ratio:.10f}'+r'\dimen0'+
                        r'\edef\picwidth{\strip@pt\dimexpr\dimen0*7200/7227\relax}'+
                        r'\edef\picheight{\strip@pt\dimexpr\dimen2*7200/7227\relax}'+
                        r'\leavevmode\hbox to \dimen0{\vrule width0pt height\dimen2 depth0pt'+
                        r'\pdfliteral{q \picwidth\space 0 0 \picheight\space 0 0 cm /'+name+
                        r' Do Q}\hss}\endgroup}')
    return '\n'.join(streams)+r'\edef\assetResources{/XObject << '+' '.join(resources)+r' >>}\pdfpageresources\expandafter{\assetResources}'+'\n'+r'\makeatletter'+'\n'+'\n'.join(commands)+'\n'+r'\makeatother'+'\n'

if __name__=='__main__':
    import sys
    p=Path(sys.argv[1])
    code=embed_assets({'Demo':p})
    tex=r'\documentclass{article}'+'\n'+code+r'\begin{document}\visualDemo{\linewidth}\end{document}'
    Path(sys.argv[2]).write_text(tex,encoding='ascii')

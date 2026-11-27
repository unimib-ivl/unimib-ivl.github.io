#!/usr/bin/env python3
"""Add a short venue name (`abbr = {...}`) to journal and conference entries in _bibliography/papers.bib.

The abbreviation is shown as a badge on the publication's fallback illustration (_includes/pub-fallback.liquid).
Entries that already have `abbr` are left untouched, so a value can always be corrected by hand.
Unknown venues get no badge: add a rule below (or an `abbr` field in the entry) and run the script again.

    python3 bin/add_venue_abbr.py            # update papers.bib in place
    python3 bin/add_venue_abbr.py --dry-run  # only list what would change and what is unknown
"""
import re
import sys
from pathlib import Path

BIB = Path(__file__).resolve().parent.parent / "_bibliography" / "papers.bib"

# (regex on the venue name, abbreviation). First match wins, so specific rules come before general ones.
CONFERENCES = [
    (r"computer vision and pattern recognition.*workshops?|\(cvprw\)|cvpr\)? workshops", "CVPRW"),
    (r"computer vision and pattern recognition|\bcvpr\b", "CVPR"),
    (r"eccv.*workshops|eccv workshops", "ECCVW"),
    (r"\beccv\b", "ECCV"),
    (r"international conference on computer vision workshops", "ICCVW"),
    (r"new trends in image analysis and processing|iciap.*workshops|\(iciapw\)", "ICIAPW"),
    (r"iciap|image analysis and processing", "ICIAP"),
    (r"icpr international workshops", "ICPRW"),
    (r"\bicpr\b|international conference on pattern recognition", "ICPR"),
    (r"berlin", "ICCE-Berlin"),
    (r"consumer electronics \(ce ws\)", "IEEE CE WS"),
    (r"\bicce\b|international conference on consumer electronic", "ICCE"),
    (r"isct|symposium on consumer technologies", "ISCT"),
    (r"computational color imaging|\bcciw", "CCIW"),
    (r"colou?r (and )?imaging conference|^\{?vii\}? color imaging conference", "CIC"),
    (r"london imaging meeting", "LIM"),
    (r"international colour association", "AIC"),
    (r"cgiv|color in graphics,? imag", "CGIV"),
    (r"color in graphics and image processing", "CGIP"),
    (r"international conference on image processing|\bicip\b|image processing, 1999", "ICIP"),
    (r"digital photography|image quality and system performance|internet imaging|color imaging (viii|ix|x)\b"
     r"|image processing: machine vision applications|multimedia content access|multimedia on mobile devices"
     r"|imaging and multimedia analytics|three-dimensional image processing|storage and retrieval for media databases"
     r"|multimedia content and mobile devices|image processing, image quality, image capture systems", "IS&T EI"),
    (r"\brtsi\b|research and technologies for society and industry", "RTSI"),
    (r"visapp|computer vision,? imaging and computer graphics theory", "VISAPP"),
    (r"international conference on learning representations", "ICLR"),
    (r"neural information processing systems", "NeurIPS"),
    (r"british machine vision", "BMVC"),
    (r"gecco|genetic and evolutionary computation conference", "GECCO"),
    (r"aixia|ai\*ia|italian association for artificial intelligence", "AIxIA"),
    (r"international conference on machine vision", "ICMV"),
    (r"multimedia \\?& expo", "ICME"),
    (r"visual communications and image processing", "VCIP"),
    (r"^\{?archiving", "Archiving"),
    (r"intelligent systems design and applications", "ISDA"),
    (r"knowledge discovery", "IC3K"),
    (r"evoiasp", "EvoIASP"),
    (r"iceis|enterprise information systems", "ICEIS"),
    (r"visual information (and information )?systems|visual information search", "VISUAL"),
    (r"acivs|advanced concepts for intelligent vision", "ACIVS"),
    (r"euvip|european workshop of visual information processing", "EUVIP"),
    (r"hawaii international conference", "HICSS"),
    (r"distributed multimedia systems", "DMS"),
    (r"\bcisis\b", "CISIS"),
    (r"\bispa\b", "ISPA"),
    (r"multimedia signal processing", "MMSP"),
    (r"advanced video and signal based surveillance", "AVSS"),
    (r"robotics and automation", "ICRA"),
    (r"^advances in information retrieval", "ECIR"),
    (r"adaptive multimedial? retrieval", "AMR"),
    (r"content-based multimedia indexing", "CBMI"),
    (r"3d data processing visualization", "3DPVT"),
    (r"multiple classifier systems", "MCS"),
    (r"biometrics: theory, applications", "BTAS"),
    (r"\bicete\b", "ICETE"),
    (r"\bsiu\b", "SIU"),
    (r"siggraph", "SIGGRAPH"),
    (r"radar conference", "RadarConf"),
    (r"egu general assembly", "EGU"),
    (r"tinyml", "tinyML"),
    (r"pervasive computing technologies for healthcare", "PervasiveHealth"),
    (r"intelligent environments", "IE"),
    (r"\bsebd\b", "SEBD"),
    (r"italian information retrieval", "IIR"),
    (r"multimedia information retrieval", "MIR"),
    (r"multimedia computing and systems", "ICMCS"),
    (r"\biscas\b", "ISCAS"),
    (r"international statistical institute", "ISI"),
    (r"axmedis", "AXMEDIS"),
    (r"computer architecture for machine perception", "CAMP"),
    (r"brain, vision,? and artificial intelligence", "BVAI"),
    (r"aixfood", "AIxFood"),
    (r"european conference on ambient intelligence", "AmI"),
    (r"aaai spring symposium", "AAAI SSS"),
    (r"ieee services", "SERVICES"),
    (r"color conference$", "Color Conf."),
    (r"conferenza nazionale del colore|proceedings of the eighth color conference", "Color Conf."),
    (r"neurips data-centric ai workshop", "NeurIPS W"),
    (r"gruppo italiano ricercatori in pattern recognition", "GIRPR"),
    (r"naples forum on service", "Naples Forum"),
    (r"scientific meeting of the italian statistical society", "SIS"),
    (r"^s\.co\.", "S.Co."),
    (r"^journal of alzheimer", "JAD"),
    (r"^journal of physics: conference series", "J. Phys. Conf. Ser."),
]

JOURNALS = [
    (r"^journal of electronic imaging$", "JEI"),
    (r"^ieee transactions on image processing$", "IEEE TIP"),
    (r"^journal of the optical society of america a$|^j\. opt\. soc\. am\. a$", "JOSA A"),
    (r"^pattern recognition letters$", "PRL"),
    (r"^pattern recognition$", "PR"),
    (r"^journal of imaging$", "J. Imaging"),
    (r"^applied sciences$", "Appl. Sci."),
    (r"^multimedia tools and applications$", "MTAP"),
    (r"^expert systems with applications$", "ESWA"),
    (r"^computer vision and image understanding$", "CVIU"),
    (r"^journal of mathematical imaging and vision$", "JMIV"),
    (r"^ieee transactions on consumer electronics$", "IEEE TCE"),
    (r"^neural computing and applications$", "NCAA"),
    (r"journal of imaging science and technology$", "JIST"),
    (r"^journal of reliable intelligent environments$", "JRIE"),
    (r"^color research (\\?&|and) application$", "Color Res. Appl."),
    (r"^cultura e scienza del colore", "Color Cult. Sci."),
    (r"^data in brief$", "Data in Brief"),
    (r"^computers in industry$", "Comput. Ind."),
    (r"^digital signal processing$", "DSP"),
    (r"^international journal on digital libraries$", "IJDL"),
    (r"^eurasip journal on advances in signal processing$", "EURASIP JASP"),
    (r"^international journal of pattern recognition and artificial intelligence", "IJPRAI"),
    (r"^machine vision and applications$", "MVA"),
    (r"^spectrochimica acta part a", "Spectrochim. Acta A"),
    (r"^acm trans\. multimedia comput|^transactions on multimedia computing", "ACM TOMM"),
    (r"^scientific data$", "Sci. Data"),
    (r"^international journal of computer vision$", "IJCV"),
    (r"^remote sensing$", "Remote Sens."),
    (r"^ieee transactions on neural networks and learning systems$", "IEEE TNNLS"),
    (r"^ieee signal processing letters$", "IEEE SPL"),
    (r"^arxiv", "arXiv"),
    (r"^artificial intelligence review$", "AI Review"),
    (r"^isprs journal of photogrammetry", "ISPRS J."),
    (r"^ieee transactions on human.machine systems$", "IEEE THMS"),
    (r"^computers & geosciences$", "Comput. Geosci."),
    (r"^genetic programming and evolvable machines$", "GPEM"),
    (r"^remote sensing applications: society", "RSASE"),
    (r"^ieee transactions on computational imaging$", "IEEE TCI"),
    (r"^quantum machine intelligence$", "QMI"),
    (r"^information fusion$", "Inf. Fusion"),
    (r"^international journal of machine learning and cybernetics$", "IJMLC"),
    (r"^computer graphics forum$", "CGF"),
    (r"^ieee transactions on pattern analysis and machine intelligence$", "IEEE TPAMI"),
    (r"^international journal of remote sensing$", "IJRS"),
    (r"^signal, image and video processing$", "SIViP"),
    (r"^information visualization$", "Inf. Vis."),
    (r"^ieee transactions on evolutionary computation$", "IEEE TEVC"),
    (r"^ieee journal of biomedical and health informatics$", "IEEE JBHI"),
    (r"^journal of cultural heritage$", "J. Cult. Herit."),
    (r"^journal of ambient intelligence and humanized computing$", "JAIHC"),
    (r"^journal of the association for information science", "JASIST"),
    (r"^information processing (\\?&|and) management$", "IP&M"),
    (r"^ieee geoscience and remote sensing letters$", "IEEE GRSL"),
    (r"^computers in human behavior$", "CHB"),
    (r"^information systems$", "Inf. Syst."),
    (r"^information sciences$", "Inf. Sci."),
    (r"^electronic letters on computer vision and image analysis$", "ELCVIA"),
    (r"^vision research$", "Vision Res."),
    (r"^recent patents on electrical engineering$", "RPEE"),
    (r"^ieee transactions on signal processing$", "IEEE TSP"),
    (r"^ieee transactions on circuits and systems for video technology$", "IEEE TCSVT"),
    (r"^computers in biology and medicine$", "CIBM"),
    (r"^digital creativity$", "Digit. Creat."),
    (r"^optical engineering$", "Opt. Eng."),
    (r"^journal of real-time image processing$", "JRTIP"),
    (r"^electronics letters$", "Electron. Lett."),
    (r"^journal of inequalities in pure and applied mathematics$", "JIPAM"),
    (r"^journal of visual languages and computing$", "JVLC"),
    (r"^image and vision computing$", "IMAVIS"),
    (r"^journal of image and graphics$", "JIG"),
    (r"^intelligent systems with applications$", "ISWA"),
    # one-word titles are short enough as they are
    (r"^(sensors|heliyon|neurocomputing|softwarex|ieee access|plos one|electronics)$", None),
]


def field(body, name):
    m = re.search(r"(?im)^\s*" + name + r"\s*=\s*\{(.*?)\}\s*,?\s*$", body, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


def abbreviate(venue, rules):
    clean = re.sub(r"[{}]", "", venue).strip()
    for pattern, abbr in rules:
        if re.search(pattern, clean, re.I):
            return abbr if abbr is not None else clean
    m = re.search(r"\(([A-Z][A-Za-z0-9&\-]{1,12})\)", clean)  # "... (ACRONYM)"
    return m.group(1) if m else None


def main():
    dry = "--dry-run" in sys.argv
    text = BIB.read_text(encoding="utf-8")
    entry_re = re.compile(r"(@(\w+)\{[^,\n]+,\n)(.*?)(?=\n@|\n% IVL category|\Z)", re.S)
    unknown, changed = [], 0

    def repl(m):
        nonlocal changed
        head, kind, body = m.group(1), m.group(2).lower(), m.group(3)
        if kind == "article":
            venue, rules = field(body, "journal"), JOURNALS
        elif kind in ("inproceedings", "conference"):
            venue, rules = field(body, "booktitle"), CONFERENCES
        else:
            return m.group(0)
        if not venue or re.search(r"(?im)^\s*abbr\s*=", body):
            return m.group(0)
        abbr = abbreviate(venue, rules)
        if not abbr:
            unknown.append(venue)
            return m.group(0)
        changed += 1
        return head + "abbr = {" + abbr + "},\n" + body

    new = entry_re.sub(repl, text)
    print(f"{changed} entries get an abbreviation; {len(unknown)} venues without one:")
    for v in sorted(set(unknown)):
        print("  -", v)
    if not dry and changed:
        BIB.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    main()

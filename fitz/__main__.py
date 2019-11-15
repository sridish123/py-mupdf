import fitz
import sys
import os


def get_list(rlist, m):
    rlist_arr = rlist.split(",")
    out_list = []
    for item in rlist_arr:
        if item.isdecimal():
            out_list.append(int(item))
            continue
        if item == "N":
            out_list.append(m - 1)
            continue
        i1, i2 = item.split("-")
        if i2 == "N":
            i2 = m - 1
        for i in range(int(i1), int(i2) + 1):
            out_list.append((i))
    return out_list


def show(args):
    doc = fitz.open(args.input)
    if not doc.isPDF:
        sys.exit("Not a PDF document.")
    size = round(os.path.getsize(args.input) / 1024, 1)
    print(
        "Filename: %s, pages: %i, objects: %i, size: %g KB"
        % (args.input, doc.pageCount, doc._getXrefLength() - 1, size)
    )
    n = doc.isFormPDF
    if n > 0:
        s = doc.getSigFlags()
        print(
            "Document contains %i root form fields and is %ssigned."
            % (n, "not " if s != 3 else "")
        )
    print()
    if args.trailer:
        print("=== PDF Trailer ===")
        print(doc.PDFTrailer())
        print()
    if args.catalog:
        print("=== PDF Catalog ===")
        xref = doc.PDFCatalog()
        print(doc.xrefObject(xref))
        print()
    if args.metadata:
        print("=== PDF Metadata ===")
        for k, v in doc.metadata.items():
            print("%s: %s" % (k, v))
        print()
    if args.xrefs:
        print("=== Object information ===")
        xrefl = get_list(args.xrefs, doc._getXrefLength())
        for xref in xrefl:
            print("%i 0 obj" % xref)
            print(doc.xrefObject(xref))
            print()
    if args.pages:
        print("=== Page information ===")
        pagel = get_list(args.pages, doc.pageCount + 1)
        for pno in pagel:
            n = pno - 1
            xref = doc._getPageXref(n)[0]
            print("Page %i:" % pno)
            print("%i 0 obj" % xref)
            print(doc.xrefObject(xref))
            print()
    doc.close()


def clean(args):
    doc = fitz.open(args.input)
    if not doc.isPDF:
        sys.exit("Not a PDF document.")
    if not args.pages:  # simple cleaning
        doc.save(
            args.output,
            garbage=args.garbage,
            deflate=args.compress,
            pretty=args.pretty,
            clean=args.sanitize,
        )
        return

    # create sub document from page numbers
    pages = get_list(args.pages, doc.pageCount + 1)
    outdoc = fitz.open()
    for pno in pages:
        n = pno - 1
        outdoc.insertPDF(doc, from_page=n, to_page=n)
    outdoc.save(
        args.output,
        garbage=args.garbage,
        deflate=args.compress,
        pretty=args.pretty,
        clean=args.sanitize,
    )
    doc.close()
    outdoc.close()
    return


def embedded_del(args):
    doc = fitz.open(args.input)
    if not doc.isPDF:
        sys.exit("Not a PDF document.")
    try:
        doc.embeddedFileDel(args.name)
    except ValueError:
        sys.exit("No embedded file named '%s'." % args.name)
    if not args.output:
        doc.saveIncr()
    else:
        doc.save(args.output, garbage=3)
    doc.close()


def embedded_get(args):
    doc = fitz.open(args.input)
    if not doc.isPDF:
        sys.exit("Not a PDF document.")
    try:
        stream = doc.embeddedFileGet(args.name)
        d = doc.embeddedFileInfo(args.name)
    except ValueError:
        sys.exit("No such embedded file '%s'." % args.name)
    filename = args.output if args.output else d["filename"]
    output = open(filename, "wb")
    output.write(stream)
    output.close()
    print("Saved entry '%s' as '%s'" % (args.name, filename))
    doc.close()


def embedded_add(args):
    doc = fitz.open(args.input)
    if not doc.isPDF:
        sys.exit("Not a PDF document.")
    try:
        name = doc.embeddedFileDel(args.name)
        sys.exit("Entry '%s' already exists in embedded files." % args.name)
    except:
        pass
    if not os.path.exists(args.file) or not os.path.isfile(args.file):
        sys.exit("No such file '%s'" % args.file)
    stream = open(args.file, "rb").read()
    filename = args.file
    ufilename = filename
    if not args.desc:
        desc = filename
    else:
        desc = args.desc
    doc.embeddedFileAdd(
        args.name, stream, filename=filename, ufilename=ufilename, desc=desc
    )
    if not args.output:
        doc.saveIncr()
    else:
        doc.save(args.output, garbage=3)
    doc.close()


def embedded_list(args):
    doc = fitz.open(args.input)
    if not doc.isPDF:
        sys.exit("Not a PDF document.")
    names = doc.embeddedFileNames()
    if not names:
        print("Document '%s' contains no embedded files." % doc.name)
        return
    if len(names) > 1:
        msg = "Document '%s' contains the following %i embedded files." % (
            doc.name,
            len(names),
        )
    else:
        msg = "Document '%s' contains the following embedded file." % doc.name
    print(msg)
    print()
    for name in names:
        if not args.detail:
            print(name)
            continue
        d = doc.embeddedFileInfo(name)
        l = max(len(k) for k in d.keys()) + 1
        for k, v in d.items():
            print(k.rjust(l), v)
        print()
    doc.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Perform basic PyMuPDF functions", prog="fitz"
    )
    subps = parser.add_subparsers(
        title="Subcommands", help="Enter 'command -h' for subcommand specific help"
    )

    # 'show' command ---------------------------------------------------------
    ps_show = subps.add_parser("show", description="Display document Information")
    ps_show.add_argument("input", type=str, help="PDF filename")
    ps_show.add_argument(
        "-cat", "--catalog", action="store_true", help="Show PDF catalog"
    )
    ps_show.add_argument(
        "-tr", "--trailer", action="store_true", help="Show PDF trailer"
    )
    ps_show.add_argument(
        "-meta", "--metadata", action="store_true", help="Show PDF metadata"
    )
    ps_show.add_argument("-xrefs", type=str, help="Show objects, format: 1,5-7,N")
    ps_show.add_argument("-pages", type=str, help="Show pages, format: 1,5-7,50-N")
    ps_show.set_defaults(func=show)

    # 'clean' command --------------------------------------------------------
    ps_clean = subps.add_parser(
        "clean", description="Optimize document or create subdocument if pages given."
    )
    ps_clean.add_argument("input", type=str, help="PDF filename")
    ps_clean.add_argument("output", type=str, help="Output PDF filename")
    ps_clean.add_argument(
        "-garbage",
        type=int,
        help="Garbage collection level",
        choices=range(5),
        default=0,
    )
    ps_clean.add_argument(
        "-com", "--compress", action="store_true", help="Compress (deflate) output"
    )
    ps_clean.add_argument(
        "-san", "--sanitize", action="store_true", help="Sanitize contents"
    )
    ps_clean.add_argument("-pretty", action="store_true", help="Prettify PDF structure")
    ps_clean.add_argument("-pages", type=str, help="Include pages, format: 1,5-7,50-N")
    ps_clean.set_defaults(func=clean)

    # 'embed-info' command ---------------------------------------------------
    ps_show = subps.add_parser("embed-info", description="List embedded files.")
    ps_show.add_argument("input", type=str, help="PDF filename")
    ps_show.add_argument("-detail", action="store_true", help="Detail information")
    ps_show.set_defaults(func=embedded_list)

    # 'embed-del' command ---------------------------------------------------
    ps_show = subps.add_parser("embed-del", description="Delete embedded file.")
    ps_show.add_argument("input", type=str, help="PDF filename")
    ps_show.add_argument(
        "-output", help="Output PDF filename, incremental save if none"
    )
    ps_show.add_argument("name", help="Name of entry to delete")
    ps_show.set_defaults(func=embedded_del)

    # 'embed-add' command ---------------------------------------------------
    ps_show = subps.add_parser("embed-add", description="Add an embedded file.")
    ps_show.add_argument("input", type=str, help="PDF filename")
    ps_show.add_argument(
        "-output", help="Output PDF filename, incremental save if none"
    )
    ps_show.add_argument("-name", help="Name of new entry")
    ps_show.add_argument("-file", help="File of new entry")
    ps_show.add_argument("-desc", help="Description of new entry")
    ps_show.set_defaults(func=embedded_add)

    # 'embed-extract' command ---------------------------------------------------
    ps_show = subps.add_parser(
        "embed-extract", description="Extract and save an embedded file."
    )
    ps_show.add_argument("input", type=str, help="PDF filename")
    ps_show.add_argument("-name", help="Name of entry")
    ps_show.add_argument("-output", help="Output filename, defaults to stored name")
    ps_show.set_defaults(func=embedded_get)

    # start program ----------------------------------------------------------
    args = parser.parse_args()
    if not hasattr(args, "func"):
        print(parser.description)
        print("enter 'fitz -h' to see basic help")
    else:
        args.func(args)


if __name__ == "__main__":
    main()

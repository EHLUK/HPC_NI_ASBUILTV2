"""
As-Built Drawing Compiler -- HPC HK2794
Streamlit web app -- v4

Features:
- Incremental build: add more ductbook PDFs to the same document
- TQ references per ECS code
- Bundled template + stamp
- Progress bar
- Password protection
"""

import os
import re
import tempfile
import shutil
import base64
from collections import Counter

import streamlit as st

# -- Config --------------------------------------------------------------------
APP_PASSWORD = "HPC2794"

# -- Page config ---------------------------------------------------------------
st.set_page_config(
    page_title="As-Built Compiler -- HK2794",
    page_icon="-",
    layout="centered",
)

# -- Password gate -------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col_l, col_t = st.columns([1, 4])
    col_l.image("data:image/png;base64,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", width=90)
    col_t.title("As-Built Compiler")
    col_t.caption("HPC HK2794 - Exentec Hargreaves")
    st.markdown("---")
    pwd = st.text_input("Enter password to continue", type="password")
    if st.button("Login", type="primary"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

# -- Import compiler -----------------------------------------------------------
try:
    from compiler import (
        extract_trn, match_drawings, render_and_stamp,
        build_docx, make_output_filename,
    )
except Exception as e:
    st.error(f"- Failed to load compiler: {e}")
    st.stop()

# -- Session state initialisation ---------------------------------------------
# We persist the build across multiple ductbook uploads using session state.
# session_state keys:
#   trn_data        -- extracted TRN data dict
#   all_matches     -- {ecs: {pdf, page}} accumulated across all batches
#   all_stamped     -- {ecs: png_bytes} accumulated across all batches
#   all_failed      -- [(ecs, reason)] accumulated
#   all_not_found   -- [ecs] still not matched
#   all_duplicates  -- {ecs: [pdfs]}
#   tq_map          -- {ecs: (tq_num, tq_desc)}
#   tmp_dir         -- persistent temp directory for stamped images
#   phase           -- 'upload' | 'tq' | 'done'
#   output_bytes    -- final docx bytes for download
#   output_filename -- filename for download

for key, default in [
    ("trn_data",        None),
    ("all_matches",     {}),
    ("all_stamped",     {}),
    ("all_failed",      []),
    ("all_not_found",   []),
    ("all_duplicates",  {}),
    ("tq_map",          {}),
    ("tmp_dir",         None),
    ("phase",           "trn_scan"),
    ("output_bytes",    None),
    ("output_filename", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# -- Helper -- ensure persistent tmp dir exists ---------------------------------
def get_tmp_dir():
    # Use a fixed path so files survive across Streamlit reruns
    if not st.session_state.tmp_dir:
        import hashlib, time
        # Create a session-specific but fixed directory
        session_hash = hashlib.md5(str(id(st.session_state)).encode()).hexdigest()[:8]
        st.session_state.tmp_dir = "/tmp/asbuilt_" + session_hash
    d = st.session_state.tmp_dir
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(d, "stamped"), exist_ok=True)
    return d

# -- Reset button --------------------------------------------------------------
def reset_build():
    tmp = st.session_state.get("tmp_dir")
    if tmp and os.path.exists(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    for key in ["trn_data","all_matches","all_stamped","all_failed",
                "all_not_found","all_duplicates","tq_map","tmp_dir",
                "phase","output_bytes","output_filename"]:
        st.session_state[key] = None if key in ["trn_data","tmp_dir",
                                                  "output_bytes","output_filename"] \
                                 else {} if key in ["all_matches","all_stamped",
                                                    "all_duplicates","tq_map"] \
                                 else [] if key in ["all_failed","all_not_found"] \
                                 else "trn_scan"

# -- Title ---------------------------------------------------------------------
LOGO_B64 = "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"
col_logo, col_title = st.columns([1, 4])
col_logo.image("data:image/png;base64," + LOGO_B64, width=110)
col_title.title("As-Built Drawing Compiler")
col_title.caption("HPC HK2794 - Exentec Hargreaves - Ductwork")
st.markdown("---")

# ------------------------------------------------------------------------------
# PHASE: UPLOAD
# ------------------------------------------------------------------------------

# ==============================================================================
# PHASE: TRN SCAN -- upload TRN first, show which ductbooks are needed
# ==============================================================================
if st.session_state.phase == "trn_scan":

    st.subheader("1 - Upload TRN")
    st.caption("Upload the TRN first and we will tell you exactly which ductbook PDFs you need.")

    trn_file = st.file_uploader("TRN PDF *(required)*", type=["pdf"],
                                help="Technical Release Note")

    if trn_file:
        if st.button("Scan TRN", type="primary"):
            with st.spinner("Reading TRN..."):
                tmp = get_tmp_dir()
                trn_path = os.path.join(tmp, "trn.pdf")
                with open(trn_path, "wb") as f:
                    f.write(trn_file.read())
                st.session_state.trn_data = extract_trn(trn_path)

            trn = st.session_state.trn_data
            ecs  = trn["ecs_codes"]
            dbs  = {}
            for e in ecs:
                db = trn["ecs_ductbook"].get(e)
                if db:
                    dbs[db] = dbs.get(db, 0) + 1

            st.success("TRN scanned -- " + str(len(ecs)) + " ECS codes found across " + str(len(dbs)) + " ductbook(s)")
            st.markdown("**You will need these ductbook PDFs:**")
            for db, count in sorted(dbs.items()):
                st.markdown("- `" + db + ".pdf` -- " + str(count) + " drawings")

            st.session_state.phase = "upload"
            st.rerun()

    st.stop()

if st.session_state.phase == "upload":

    # If we already have a partial build, show status and allow adding more
    has_partial = bool(st.session_state.all_matches)

    if has_partial:
        trn  = st.session_state.trn_data
        done = len(st.session_state.all_stamped)
        todo = len(st.session_state.all_not_found)
        st.success(
            f"- Build in progress -- **{done} drawings** embedded so far.  "
            f"{'**' + str(todo) + ' still needed.**' if todo else 'All drawings matched!'}"
        )
        if todo:
            missing_db = Counter(
                trn["ecs_ductbook"].get(c, "unknown")
                for c in st.session_state.all_not_found
            )
            st.markdown("**Still need these ductbook PDFs:**")
            for db, cnt in sorted(missing_db.items()):
                st.markdown(f"- `{db}.pdf` -- {cnt} drawings")
        st.markdown("---")

    # -- Upload section --------------------------------------------------------
    if not has_partial:
        st.subheader("1 - Upload files")
    else:
        st.subheader("- Add more drawing PDFs")

    col1, col2 = st.columns(2)

    with col1:
        # TRN already scanned before reaching this phase
        trn_file = None
        trn_d = st.session_state.trn_data
        st.info("TRN: **" + trn_d["delivery_ref"] + "** -- " + str(len(trn_d["ecs_codes"])) + " ECS codes")

        # Show which ductbooks are still needed
        trn_d    = st.session_state.trn_data
        need_dbs = {}
        for e in trn_d["ecs_codes"]:
            db = trn_d["ecs_ductbook"].get(e)
            if db and e not in st.session_state.all_matches:
                need_dbs[db] = need_dbs.get(db, 0) + 1
        done_dbs = {}
        for e in st.session_state.all_matches:
            db = trn_d["ecs_ductbook"].get(e)
            if db:
                done_dbs[db] = done_dbs.get(db, 0) + 1

        if done_dbs:
            for db, cnt in sorted(done_dbs.items()):
                st.markdown("- [x] `" + db + "` -- " + str(cnt) + " drawings done")
        if need_dbs:
            st.markdown("**Still needed:**")
            for db, cnt in sorted(need_dbs.items()):
                st.markdown("- [ ] `" + db + ".pdf` -- " + str(cnt) + " drawings")

        drawing_files = st.file_uploader(
            "Ductwork Drawing PDFs *(required)*",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload one or more ductbook PDFs to add to the build.",
        )

    with col2:
        tmp = get_tmp_dir()
        template_saved = os.path.exists(os.path.join(tmp, "template.docx"))
        stamp_saved    = os.path.exists(os.path.join(tmp, "stamp.png"))

        if template_saved:
            st.success("+ Word template uploaded")
            template_file = None
        else:
            template_file = st.file_uploader(
                "As-Built Word template (.docx) *(required)*", type=["docx"]
            )

        if stamp_saved:
            st.success("+ Conformance stamp uploaded")
            stamp_file = None
        else:
            stamp_file = st.file_uploader(
                "Conformance Stamp PNG *(required)*", type=["png"],
                help="Portrait red-border stamp image"
            )

    # File size warning
    if drawing_files:
        total_mb = sum(f.size for f in drawing_files) / 1_048_576
        if total_mb > 80:
            st.error(
                f"-- {total_mb:.0f} MB uploaded -- may exceed memory limit. "
                f"Try 1-2 PDFs at a time."
            )
        elif total_mb > 40:
            st.warning(f"-- {total_mb:.0f} MB uploaded -- may take 3-5 minutes.")

    st.markdown("---")

    # Readiness check
    template_ready = template_file is not None or template_saved
    stamp_ready    = stamp_file    is not None or stamp_saved

    missing = []
    # TRN always loaded before reaching this phase
    if not drawing_files:                 missing.append("at least one drawing PDF")
    if not template_ready:                missing.append("Word template")
    if not stamp_ready:                   missing.append("conformance stamp PNG")

    if missing:
        st.info(f"Still needed: {', '.join(missing)}")

    col_btn1, col_btn2 = st.columns([3, 1])
    scan_btn = col_btn1.button(
        "-  Scan Drawing PDFs",
        disabled=bool(missing),
        type="primary",
    )
    if has_partial:
        if col_btn2.button("- Start Over", type="secondary"):
            reset_build()
            st.rerun()

    if scan_btn and not missing:
        status_text  = st.empty()
        progress_bar = st.progress(0)

        def upd(msg, pct):
            status_text.info(f"- {msg}")
            progress_bar.progress(int(pct))

        tmp = get_tmp_dir()

        try:
            upd("Saving files-", 2)

            # Save template
            template_path = os.path.join(tmp, "template.docx")
            if not os.path.exists(template_path):
                with open(template_path, "wb") as f:
                    f.write(template_file.read())

            # Save stamp
            stamp_path = os.path.join(tmp, "stamp.png")
            if not os.path.exists(stamp_path):
                with open(stamp_path, "wb") as f:
                    f.write(stamp_file.read())

            # TRN already extracted in trn_scan phase - nothing to do here

            trn_data     = st.session_state.trn_data
            ecs_codes    = trn_data["ecs_codes"]
            ecs_ductbook = trn_data["ecs_ductbook"]

            upd(f"Found {len(ecs_codes)} ECS codes", 15)

            # Save drawing PDFs
            drawing_paths = []
            for df in drawing_files:
                dp = os.path.join(tmp, df.name)
                with open(dp, "wb") as f:
                    f.write(df.read())
                drawing_paths.append(dp)

            # Match drawings -- only look for codes not yet matched
            already_matched = set(st.session_state.all_matches.keys())
            remaining_codes = [e for e in ecs_codes if e not in already_matched]

            n_pdfs = len(drawing_paths)
            def scan_prog(msg):
                m = re.search(r'\((\d+)/', msg)
                i = int(m.group(1)) if m else 1
                upd(msg, 15 + int(i / n_pdfs * 35))

            new_matches, not_found, new_dupes = match_drawings(
                remaining_codes, ecs_ductbook, drawing_paths,
                progress=scan_prog
            )
            upd(f"Matched {len(new_matches)} new drawings", 50)

            # Merge into session state
            st.session_state.all_matches.update(new_matches)
            st.session_state.all_duplicates.update(new_dupes)

            # not_found = remaining codes still unmatched after this batch
            still_not_found = [e for e in ecs_codes
                               if e not in st.session_state.all_matches]
            st.session_state.all_not_found = still_not_found

            # Render + stamp new matches
            total_new = len(new_matches)
            def stamp_prog(msg, pct=None):
                if pct is not None:
                    upd(msg, 50 + int(pct * 0.45))
                else:
                    upd(msg, 72)

            new_stamped, new_failed = render_and_stamp(
                new_matches, stamp_path, tmp,
                progress=stamp_prog,
                tq_map=st.session_state.tq_map or None
            )

            # Store paths to stamped images - files live in persistent tmp_dir/stamped


            for ecs, path in new_stamped.items():
                st.session_state.all_stamped[ecs] = path



            st.session_state.all_failed.extend(new_failed)

            upd("Done scanning!", 100)
            progress_bar.progress(100)
            status_text.success(
                f"- Scanned -- {len(new_matches)} new drawings found. "
                f"{'Fill in TQ references below.' if not has_partial else 'Ready to build.'}"
            )

            # Move to TQ phase
            st.session_state.phase = "tq"
            st.rerun()

        except Exception as e:
            status_text.error(f"- Error: {e}")
            import traceback
            st.code(traceback.format_exc())

# ------------------------------------------------------------------------------
# PHASE: TQ + BUILD
# ------------------------------------------------------------------------------
elif st.session_state.phase == "tq":

    trn_data     = st.session_state.trn_data
    ecs_codes    = trn_data["ecs_codes"]
    ecs_ductbook = trn_data["ecs_ductbook"]
    all_matches  = st.session_state.all_matches
    all_stamped  = st.session_state.all_stamped
    not_found    = st.session_state.all_not_found

    total_done = len(all_stamped)
    total_ecs  = len(ecs_codes)

    st.subheader("2b - TQ References (optional)")
    st.caption(
        "For any ECS code affected by a Technical Query, enter the TQ number "
        "and description. Leave blank to skip."
    )

    # Show ECS codes grouped by ductbook
    matched_dbs = []
    for e in ecs_codes:
        db = ecs_ductbook.get(e)
        if db and db not in matched_dbs and e in all_matches:
            matched_dbs.append(db)

    for db in matched_dbs:
        db_codes = [e for e in ecs_codes
                    if ecs_ductbook.get(e) == db and e in all_matches]
        with st.expander(f"{db} -- {len(db_codes)} drawings", expanded=False):
            cols_h = st.columns([3, 2, 4])
            cols_h[0].markdown("**ECS Code**")
            cols_h[1].markdown("**TQ Number**")
            cols_h[2].markdown("**Description**")
            for ecs in db_codes:
                existing_tq = st.session_state.tq_map.get(ecs, ("", ""))
                cols = st.columns([3, 2, 4])
                cols[0].text(ecs)
                tq_num = cols[1].text_input(
                    "TQ", key=f"tq_num_{ecs}",
                    label_visibility="collapsed",
                    placeholder="e.g. TQ137",
                    value=existing_tq[0],
                )
                tq_desc = cols[2].text_input(
                    "Desc", key=f"tq_desc_{ecs}",
                    label_visibility="collapsed",
                    placeholder="Brief description",
                    value=existing_tq[1],
                )
                if tq_num.strip():
                    st.session_state.tq_map[ecs] = (tq_num.strip(), tq_desc.strip())
                elif ecs in st.session_state.tq_map:
                    del st.session_state.tq_map[ecs]

    tq_count = len(st.session_state.tq_map)
    if tq_count:
        st.info(f"-- {tq_count} TQ reference(s) will be applied to drawings.")

    st.markdown("---")
    st.subheader("3 - Build Document")

    # Summary metrics
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("ECS codes in TRN",  total_ecs)
    col_b.metric("Drawings ready",    total_done)
    col_c.metric("Still missing",     len(not_found))

    if not_found:
        missing_db = Counter(ecs_ductbook.get(c, "unknown") for c in not_found)
        lines = "\n".join(
            f"- `{db}.pdf` -- {cnt} drawings"
            for db, cnt in sorted(missing_db.items())
        )
        st.warning(
            f"-- {len(not_found)} drawings not yet found. "
            f"You can build now (partial) or go back and add more PDFs.\n\n{lines}"
        )

    col_b1, col_b2, col_b3 = st.columns([2, 2, 1])
    build_btn   = col_b1.button("-  Build Document Now", type="primary")
    addmore_btn = col_b2.button("- Add More Drawing PDFs")
    restart_btn = col_b3.button("- Start Over")

    if restart_btn:
        reset_build()
        st.rerun()

    if addmore_btn:
        st.session_state.phase = "upload"
        st.rerun()

    if build_btn:
        status_text  = st.empty()
        progress_bar = st.progress(0)

        def upd(msg, pct):
            status_text.info(f"- {msg}")
            progress_bar.progress(int(pct))

        tmp = get_tmp_dir()

        try:
            # Re-apply TQ map -- need to re-render affected drawings
            tq_map = st.session_state.tq_map
            if tq_map:
                upd(f"Applying {len(tq_map)} TQ reference(s) to drawings-", 10)
                stamp_path = os.path.join(tmp, "stamp.png")
                tq_matches = {e: all_matches[e] for e in tq_map if e in all_matches}
                if tq_matches:
                    tq_stamped, _ = render_and_stamp(
                        tq_matches, stamp_path, tmp,
                        tq_map=tq_map,
                        progress=lambda msg, pct=None: upd(msg, 15)
                    )
                    stamped_dir = os.path.join(tmp, "stamped")
                    os.makedirs(stamped_dir, exist_ok=True)
                    for ecs, path in tq_stamped.items():
                        dest = os.path.join(stamped_dir, os.path.basename(path))
                        if path != dest:
                            import shutil as _sh
                            _sh.copy2(path, dest)
                        st.session_state.all_stamped[ecs] = dest

            upd("Building Word document-", 30)

            # Stamped images are already on disk as paths
            stamped_paths = dict(st.session_state.all_stamped)

            template_path   = os.path.join(tmp, "template.docx")
            output_filename = make_output_filename(trn_data)
            output_path     = os.path.join(tmp, output_filename)

            build_docx(
                template_path, trn_data, all_matches,
                stamped_paths, output_path, tmp,
                progress=lambda m: upd(m, 70)
            )

            upd("Done!", 100)
            progress_bar.progress(100)
            status_text.success("- As-Built document built successfully!")

            with open(output_path, "rb") as f:
                st.session_state.output_bytes    = f.read()
            st.session_state.output_filename = output_filename
            st.session_state.phase           = "done"
            st.rerun()

        except Exception as e:
            status_text.error(f"- Error: {e}")
            import traceback
            st.code(traceback.format_exc())

# ------------------------------------------------------------------------------
# PHASE: DONE
# ------------------------------------------------------------------------------
elif st.session_state.phase == "done":

    trn_data     = st.session_state.trn_data
    ecs_codes    = trn_data["ecs_codes"]
    ecs_ductbook = trn_data["ecs_ductbook"]
    all_stamped  = st.session_state.all_stamped
    not_found    = st.session_state.all_not_found
    all_matches  = st.session_state.all_matches

    st.success("- As-Built document ready to download!")
    st.markdown("---")

    # Metrics
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("ECS codes in TRN",  len(ecs_codes))
    col_b.metric("Drawings embedded", len(all_stamped))
    col_c.metric("TQ references",     len(st.session_state.tq_map))

    # Warnings
    if st.session_state.all_duplicates:
        lines = "\n".join(
            f"- `{ecs}` in: {', '.join(Path(p).name for p in pdfs)}"
            for ecs, pdfs in st.session_state.all_duplicates.items()
        )
        st.warning(f"-- {len(st.session_state.all_duplicates)} duplicate ECS codes:\n\n{lines}")

    if not_found:
        missing_db = Counter(ecs_ductbook.get(c, "unknown") for c in not_found)
        lines = "\n".join(
            f"- `{db}.pdf` -- {cnt} drawings"
            for db, cnt in sorted(missing_db.items())
        )
        st.warning(f"-- {len(not_found)} drawings not included:\n\n{lines}")

    if st.session_state.all_failed:
        lines = "\n".join(
            f"- `{ecs}` -- {reason}"
            for ecs, reason in st.session_state.all_failed
        )
        st.error(f"- {len(st.session_state.all_failed)} drawing(s) failed:\n\n{lines}")

    # Appendices summary
    matched_dbs = []
    for e in ecs_codes:
        db = ecs_ductbook.get(e)
        if db and db not in matched_dbs and e in all_stamped:
            matched_dbs.append(db)
    if matched_dbs:
        st.markdown("**Appendices in document:**")
        rows = []
        for i, db in enumerate(matched_dbs):
            n = sum(1 for e in ecs_codes
                    if ecs_ductbook.get(e) == db and e in all_stamped)
            tqs = sum(1 for e in ecs_codes
                      if ecs_ductbook.get(e) == db
                      and e in st.session_state.tq_map)
            rows.append({
                "Appendix": i+1,
                "Ductbook": db,
                "Drawings": n,
                "TQ refs": tqs if tqs else 0,
            })
        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Download
    st.download_button(
        label=f"--  Download  {st.session_state.output_filename}",
        data=st.session_state.output_bytes,
        file_name=st.session_state.output_filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
    )

    st.markdown("")
    col_b1, col_b2 = st.columns(2)

    # Add more drawings -- go back to upload keeping all state
    if col_b1.button("- Add More Drawing PDFs & Rebuild"):
        st.session_state.phase = "upload"
        st.rerun()

    # Start completely fresh
    if col_b2.button("- Start New As-Built"):
        reset_build()
        st.rerun()

# -- Footer --------------------------------------------------------------------
st.markdown("---")
col_f1, col_f2 = st.columns([4, 1])
col_f1.caption("Exentec Hargreaves - HPC HK2794 - As-Built Compiler v4")
if col_f2.button("Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

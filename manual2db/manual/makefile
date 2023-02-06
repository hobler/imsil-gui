# ----------------------------------------------------------------------
# Makefile for the generation of manual.pdf
#
# manual.pdf and auxiliary files are generated in the work directory
#
# "make" |
# "make all"            ... make manual.pdf
#
# "make clean"          ... delete the work manual directory 
#
# 29-Jan-2016  G.Hobler  creation
# ----------------------------------------------------------------------


# Macros ---------------------------------------------------------------

#BRANCH=$(shell git describe --tags --exact-match || git symbolic-ref --short HEAD)
#BRANCH=$(shell if test "$(shell git status -z)"; then git symbolic-ref --short HEAD; else git describe --tags --exact-match || git symbolic-ref --short HEAD; fi)
BRANCH=$(shell git symbolic-ref --short HEAD)
OUTDIR=${HOME}/work/imsil/${BRANCH}/manual
PDF=${OUTDIR}/manual.pdf
DEP=manual.tex manualstyle.tex \
titlepage.tex \
introduction.tex \
iontarget.tex iontarg_beam.tex iontarg_material.tex iontarg_geometry.tex \
physics.tex phys_collisions.tex phys_damage.tex phys_det.tex phys_estop.tex \
phys_potential.tex phys_rbs.tex phys_sputter.tex \
files.tex fil_input.tex fil_out.tex fil_his1d.tex fil_his2d.tex fil_his3d.tex fil_misc.tex \
records.tex rec_atoms.tex rec_crystal.tex rec_damage.tex rec_geometry.tex rec_ions.tex \
rec_material.tex rec_output.tex rec_separ.tex rec_setup.tex rec_snpar.tex \
scripts.tex scr_run.tex scr_read.tex \
ex_impl1d.tex ex_impl2d.tex ex_multi.tex ex_spot.tex ex_sput_stat.tex ex_sput_dyn.tex \
ex_rbs.tex \
manual.bib imsil.bib \
makefile

# Targets --------------------------------------------------------------

all : ${PDF}

${PDF} : ${DEP}
	if test ! -d ${OUTDIR}; then mkdir -p ${OUTDIR}; fi
	if test -f ${OUTDIR}/manual.aux; then rm ${OUTDIR}/manual.aux; fi
	if test -f ${OUTDIR}/imsil.aux; then rm ${OUTDIR}/imsil.aux; fi
	if test -f ${OUTDIR}/manual.bbl; then rm ${OUTDIR}/manual.bbl; fi
	if test -f ${OUTDIR}/imsil.bbl; then rm ${OUTDIR}/imsil.bbl; fi
	echo "Running latex..."
	pdflatex -output-directory=${OUTDIR} manual.tex
	echo ${CURDIR}
	ln -sf ${CURDIR}/manual.bib ${OUTDIR}/manual.bib
	ln -sf ${CURDIR}/imsil.bib ${OUTDIR}/imsil.bib
	cd ${OUTDIR}; bibtex manual; bibtex imsil
	echo ${CURDIR}
	cd -
	pdflatex -output-directory=${OUTDIR} manual.tex
	pdflatex -output-directory=${OUTDIR} manual.tex
	
clean :
	-rm -rf ${OUTDIR}

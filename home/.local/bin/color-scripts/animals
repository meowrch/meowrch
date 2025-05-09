#!/usr/bin/env bash

# ============
# ASCII ANIMAL
# ============

# ANSI COLOUR CODES
RD='\x1B[0;31m'
GR='\x1B[0;32m'
YL='\x1B[1;33m'
OR='\x1B[0;33m'
BL='\x1B[0;34m'
LBL='\x1B[1;34m'
CY='\x1B[1;36m'
NC='\x1B[0m' # No Color

echo ""

# LIZARD ####################################################################
# Adapted from: http://chris.com/ascii/index.php?art=animals/reptiles/lizards - Glo Pearl
liz1="${GR}          ${YL}O${GR}--${YL}O${GR}^^^^^^^^^^^^\________${NC}\n"
liz2="${GR}          \__/||-------||---------~${NC}\n"
liz="$liz1$liz2"

# DINOSAUR ##################################################################
# Adapted from: http://chris.com/ascii/index.php?art=animals/reptiles/dinosaurs
din1="${OR}                             __ ${NC}\n"
din2="${OR}                           / ${LBL}°${OR}_)${NC}\n"
din3="${OR}                _.----. _ /  /  ${NC}\n"
din4="${OR}              /           ../   ${NC}\n"
din5="${OR}          ___/ (   | ( ..|      ${NC}\n"
din6="${OR}        -------|_|--|_|         ${NC}\n"
din="$din1$din2$din3$din4$din5$din6"

# DUCK #####################################################################
# Adapted from: http://textart.io/art/tag/duck
duc1="                __           \n"
duc2="            ___( o)${OR}>${NC}         \n"
duc3="            \ <_. )    ${GR}V${NC}     \n"
duc4="        ${BL}~~~~~${NC}\`---'${BL}~~~~~${GR}|${BL}~~~${NC}\n"
duc="$duc1$duc2$duc3$duc4"

# PEACOCK #################################################################
# Adapted from: http://www.chris.com/ascii/joan/www.geocities.com/SoHo/7373/birds.html#peacockk
pea1="                ${CY}_   _          ${NC}\n"
pea2="             ${GR}__${CY}/o'V'o\\\\${GR}__       ${NC}\n"
pea3="          ${CY}__${GR}/o ${CY}\\  :  / ${GR}o\\\\${CY}__    ${NC}\n"
pea4="         ${CY}/o ${GR}\`.  ${CY}\ : /  ${GR}.' ${CY}o\\   ${NC}\n"
pea5="        ${GR}_${CY}\\    ${GR}'. ${NC}/\"\\ ${GR}.'    ${CY}/${GR}_  ${NC}\n"
pea6="       ${GR}/o${CY} \`-._  ${GR}'${NC}\\\v/${GR}'  ${CY}_.-\` ${GR}o\\\ ${NC}\n"
pea7="       ${GR}\\_${CY}     \`-.${NC}/ \\\\${CY}.-\`     ${GR}_/ ${NC}\n"
pea8="      ${CY}/o${NC} ${GR}\`\`---._${NC}/   \\\\${GR}_.---'' ${CY}o\\\\${NC}\n"
pea9="      ${CY}\_________${NC}\   /${CY}_________/${NC}\n"
pea10="                '\_/'          \n"
pea11="                ${OR}_|_|_${NC}          \n"
pea="$pea1$pea2$pea3$pea4$pea5$pea6$pea7$pea8$pea9$pea10$pea11"

# SQUIRREL ################################################################
# Adapted from: http://www.heartnsoul.com/ascii_art/squirrels.txt
squ1="${OR}        ,;;:;,          ${NC}\n"
squ2="${OR}          ;;;;;         ${NC}\n"
squ3="${OR}         ,:;;:;    ,'=. ${NC}\n"
squ4="${OR}         ;:;:;' .=\" ,'_\\\\${NC}\n"
squ5="${OR}         ':;:;,/  ,__:=${RD}@${NC}\n"
squ6="${OR}          ';;:;  =./)_  ${NC}\n"
squ7="${OR}            \`\"=\_  )_\"\` ${NC}\n"
squ8="${OR}                 \`\`'\"\`  ${NC}\n"
squ="$squ1$squ2$squ3$squ4$squ5$squ6$squ7$squ8"

# Generate random number
RAND=$((((RANDOM + RANDOM) % 4) + 1))

case "$RAND" in
  1) echo -e "$liz"
    ;;
  2) echo -e "$din"
    ;;
  3) echo -e "$duc"
    ;;
  4) echo -e "$pea"
    ;;
#  5) echo -e "$squ"
#    ;;
  *)
    ;;
esac

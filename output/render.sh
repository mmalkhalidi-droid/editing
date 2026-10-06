#!/bin/bash
set -e
U=/root/.claude/uploads/d12b268e-dc69-50d2-a635-cb7b37c24818
P=$(ls $U/414f*.MP4); SC=$(ls $U/a4f3*.mov); O=$(ls $U/cd88*.MOV)
S=/tmp/claude-0/-home-user-editing/d12b268e-dc69-50d2-a635-cb7b37c24818/scratchpad
OUT=/home/user/editing/output/final.mp4
PD=135.098; X1=15.8; X2=$(echo "$PD-0.4" | bc)   # crossfade offsets
EXPL=$(echo "$PD-$X1" | bc)                       # explanation stream length
# circle masks (anti-aliased)
ffmpeg -v error -y -f lavfi -i color=black:270x270 -vf "format=gray,geq=lum='255*clip(135.5-hypot(X-134.5,Y-134.5),0,1)'" -frames:v 1 $S/mask270.png
ffmpeg -v error -y -f lavfi -i color=black:262x262 -vf "format=gray,geq=lum='255*clip(131.5-hypot(X-130.5,Y-130.5),0,1)'" -frames:v 1 $S/mask262.png
FIT='scale=1080:1920:force_original_aspect_ratio=decrease,setsar=1'
COVER='scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,eq=brightness=-0.08,setsar=1'
ffmpeg -hide_banner -y -i "$P" -i "$SC" -i "$O" -loop 1 -i $S/mask270.png -loop 1 -i $S/mask262.png -filter_complex "
[0:v]fps=30,setsar=1,split=2[pv0][pv1];
[pv0]trim=0:16.2,setpts=PTS-STARTPTS,split[pa][pb];[pb]$COVER[pbg];[pa]$FIT[pfg];[pbg][pfg]overlay=(W-w)/2:(H-h)/2,format=yuv420p,fps=30,settb=1/30[intro];
[1:v]fps=30,setsar=1,trim=0:$EXPL,setpts=PTS-STARTPTS,split[sa][sb];[sb]$COVER[sbg];[sa]$FIT[sfg];[sbg][sfg]overlay=(W-w)/2:(H-h)/2,tpad=stop_mode=clone:stop_duration=$EXPL,trim=0:$EXPL[scr];
[pv1]trim=start=$X1,setpts=PTS-STARTPTS,crop=340:340:118:215,scale=262:262,format=rgba[face];
[4:v]format=gray,trim=0:$EXPL[m262];[face][m262]alphamerge[facec];
color=white:270x270:r=30:d=$EXPL,format=rgba[disk];[3:v]format=gray,trim=0:$EXPL[m270];[disk][m270]alphamerge[ring];
[ring][facec]overlay=4:4:shortest=1[circle];
[scr][circle]overlay=40:40:shortest=1,format=yuv420p,fps=30,settb=1/30[expl];
[2:v]fps=30,setsar=1,split[o1][o2];
[o1]trim=0:12.4,setpts=PTS-STARTPTS,crop=552:924:76:34,split[oa][ob];[ob]$COVER[obg];[oa]$FIT[ofg];[obg][ofg]overlay=(W-w)/2:(H-h)/2[oc1];
[o2]trim=start=12.4,setpts=PTS-STARTPTS,split[oc][od];[od]$COVER[odg];[oc]$FIT[ofg2];[odg][ofg2]overlay=(W-w)/2:(H-h)/2[oc2];
[oc1][oc2]concat=n=2:v=1,format=yuv420p,fps=30,settb=1/30[outro];
[intro][expl]xfade=transition=fade:duration=0.4:offset=$X1[v1];
[v1][outro]xfade=transition=fade:duration=0.4:offset=$X2[v];
[0:a]aresample=48000,atrim=0:$PD,asetpts=PTS-STARTPTS[a0];[2:a]aresample=48000[a2];
[a0][a2]acrossfade=d=0.4:c1=tri:c2=tri[a]
" -map "[v]" -map "[a]" -r 30 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -profile:v high -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"

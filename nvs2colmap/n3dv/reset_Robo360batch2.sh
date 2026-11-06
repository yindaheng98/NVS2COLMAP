#!/bin/bash
set -e
rm -rf data/Robo360/batch2/*/frame*
# batch2 opens with a sync flash. --start-number is the first 1-based source
# frame after that flash. Extracted frames are renumbered from frame1.
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_bottle_flip_fast --video-extension MP4 --start-number 14 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_bread_fall --video-extension MP4 --start-number 13 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_cucumber_skewer --video-extension MP4 --start-number 18 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_dish_soap --video-extension MP4 --start-number 15 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_fold_tshirt --video-extension MP4 --start-number 17 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_fortune_cookie --video-extension MP4 --start-number 17 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_gold_rope_in_basket_2 --video-extension MP4 --start-number 15 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_plastic_air_bag --video-extension MP4 --start-number 18 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_plugboard --video-extension MP4 --start-number 21 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_pour_orange_juice_2 --video-extension MP4 --start-number 19 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_put_bread_in_plastic_bag --video-extension MP4 --start-number 16 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_sand_pour --video-extension MP4 --start-number 14 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_sprite_pour_2 --video-extension MP4 --start-number 19 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_sprite_stack --video-extension MP4 --start-number 19 "$@"
python -m nvs2colmap.n3dv --path data/Robo360/batch2/xarm6_unfold_tshirt --video-extension MP4 --start-number 20 "$@"

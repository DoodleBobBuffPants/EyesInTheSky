# get function to test
from frontend.MediaPlayer import MediaPlayer as Mp
from backend.movement import FollowingDrone

# noinspection SpellCheckingInspection
testvid = "testvideo.mp4"  # test video - should use rtp://localhost:55004
mp = Mp()
drone = FollowingDrone()
mp.play_vid(testvid, drone)

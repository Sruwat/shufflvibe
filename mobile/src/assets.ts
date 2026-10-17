import type { ImageSourcePropType } from "react-native";

export const welcomeHeroArtwork = require("../assets/welcome_night_shape.png");
export const homeCityArtwork = require("../assets/home_city_night.png");
export const shfflOpeningAnimation = require("../assets/brand_opening.gif");
export const shfflWordmark = require("../assets/shffl_wordmark.png");

// Static Metro imports keep the artwork bundled for offline APK use.
export const preferenceArtwork: Record<string, ImageSourcePropType> = {
  "P-FOOD": require("../assets/preferences/food.png"),
  "P-LIVE": require("../assets/preferences/live_music.png"),
  "P-POL": require("../assets/preferences/dress_prefrence.png"),
  "P-SCEN": require("../assets/preferences/beautiful_places.png"),
  "P-NOV": require("../assets/preferences/new_places.png"),
  "P-HERIT": require("../assets/preferences/old_places.png"),
};

export const dressSenseArtwork = {
  classy: require("../assets/preferences/classy_dress_pref.png"),
  current: require("../assets/preferences/current_dress_pref.png"),
};

export const vibeCardArtwork: Record<string, ImageSourcePropType> = {
  "V-ENRG-A": require("../assets/vibes/V-ENRG-A_v1.png"),
  "V-ENRG-B": require("../assets/vibes/V-ENRG-B_v1.png"),
  "V-AFFIL-A": require("../assets/vibes/V-AFFIL-A_v1.png"),
  "V-AFFIL-B": require("../assets/vibes/V-AFFIL-B_v1.png"),
  "V-CROWD-A": require("../assets/vibes/V-CROWD-A_v1.png"),
  "V-CROWD-B": require("../assets/vibes/V-CROWD-B_v1.png"),
  "V-TALK-A": require("../assets/vibes/V-TALK-A_v1.png"),
  "V-TALK-B": require("../assets/vibes/V-TALK-B_v1.png"),
  "V-ROAM-A": require("../assets/vibes/V-ROAM-A_v1.png"),
  "V-ROAM-B": require("../assets/vibes/V-ROAM-B_v1.png"),
  "V-MOVE-A": require("../assets/vibes/V-MOVE-A_v1.png"),
  "V-MOVE-B": require("../assets/vibes/V-MOVE-B_v1.png"),
  "V-GAMES-A": require("../assets/vibes/V-GAMES-A_v1.png"),
  "V-GAMES-B": require("../assets/vibes/V-GAMES-B_v1.png"),
  "V-RAMP-A": require("../assets/vibes/V-RAMP-A_v1.png"),
  "V-RAMP-B": require("../assets/vibes/V-RAMP-B_v1.png"),
};

export const venueArtwork: Record<string, ImageSourcePropType> = {
  "Sidecar, GK-2": require("../assets/preferences/food.png"),
  "Sunder Nursery": require("../assets/preferences/beautiful_places.png"),
  "Piano Man Jazz Club": require("../assets/preferences/live_music.png"),
  "Majnu ka Tila Lane": require("../assets/preferences/old_places.png"),
};

export const revealArtwork: Record<string, ImageSourcePropType> = {
  "Peak Mingler": require("../assets/reveal/peak_mingler.png"),
  "Peak Table-Talker": require("../assets/reveal/peak_table_talker.png"),
  "Peak Crowd-Chaser": require("../assets/reveal/peak_crowd_chaser.png"),
  "Peak Floor-Filler": require("../assets/reveal/peak_floor_filler.png"),
  "Peak Score-Keeper": require("../assets/reveal/peak_score_keeper.png"),
  "Quiet Table-Talker": require("../assets/reveal/quiet_table_talker.png"),
  "Quiet One Insider": require("../assets/reveal/quiet_one_insider.png"),
  "Nomad Floor-Filler": require("../assets/reveal/nomad_floor_filler.png"),
  "Nomad Score-Keeper": require("../assets/reveal/nomad_score_keeper.png"),
  "Slow-Build Table-Talker": require("../assets/reveal/slow_build_table_talker.png"),
  "Slow-Build Floor-Filler": require("../assets/reveal/slow_build_floor_filler.png"),
  "Talking Insider": require("../assets/reveal/talking_insider.png"),
  "Big-Room Climber": require("../assets/reveal/big_room_climber.png"),
  "Moving Crowd-Chaser": require("../assets/reveal/moving_crowd_chaser.png"),
  "Arcade Mingler": require("../assets/reveal/arcade_mingler.png"),
  "Seated Table-Talker": require("../assets/reveal/seated_table_talker.png"),
  "Straight-In Crowd-Chaser": require("../assets/reveal/straight_in_crowd_chaser.png"),
  "Low-Key Settler": require("../assets/reveal/low_key_settler.png"),
  "Low-Key Insider": require("../assets/reveal/low_key_insider.png"),
  "No-Games Table-Talker": require("../assets/reveal/no_games_table_talker.png"),
  "Inner-Circle Floor-Filler": require("../assets/reveal/inner_circle_floor_filler.png"),
};

export const profileBadges: Record<string, ImageSourcePropType> = {
  Foodie: require("../assets/profile/foodie.png"),
  "Gig-Goer": require("../assets/profile/gig_goer.png"),
  "Dressed For It": require("../assets/profile/dressed_for_it.png"),
  Hype: require("../assets/profile/hype.png"),
  "Good Eye": require("../assets/profile/good_eye.png"),
  "First Timer": require("../assets/profile/first_timer.png"),
  "Old Soul": require("../assets/profile/old_soul.png"),
};

export const profileBanner = require("../assets/profile/profile_badges_banner.png");
export const profileHeaderArtwork = require("../assets/profile/profile_header_art.png");

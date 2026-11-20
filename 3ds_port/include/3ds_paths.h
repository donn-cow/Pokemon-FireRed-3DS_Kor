#ifndef CTR_PATHS_H
#define CTR_PATHS_H

/* The port's folder on the SD card: the executable, save, settings and data
   pack all live there. The Korean build has its own so it never touches the
   English one's. */
#ifdef CTR_SD_KO
#define CTR_SD_DIRNAME "firered3ds-ko"
#else
#define CTR_SD_DIRNAME "firered3ds"
#endif

#define CTR_SD_DIR "sdmc:/3ds/" CTR_SD_DIRNAME           /* no trailing slash */
#define CTR_SD_ROOT CTR_SD_DIR "/"                        /* "sdmc:/3ds/.../" */
#define CTR_SD_SHOWN "/3ds/" CTR_SD_DIRNAME "/"           /* in messages */

#endif

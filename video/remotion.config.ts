/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import path from "path";
import os from "os";
import { Config } from "@remotion/cli/config";
import { enableTailwind } from '@remotion/tailwind-v4';

const baseDir = path.join(os.homedir(), "Videos", "TeacherOS");

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setOutputLocation(baseDir);
Config.setPublicDir(path.join(baseDir, "assets"));
Config.overrideWebpackConfig(enableTailwind);

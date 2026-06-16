#!/bin/bash

# Define clear styling colors for terminal feedback
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔮 Starting Grimoire Automated Highlights Sync...${NC}"

# 1. Verification Check: Ensure Calibre is closed to prevent database corruption
if pgrep -x "calibre" > /dev/null; then
    echo -e "${RED}⚠️ Error: Calibre Desktop App is currently open! Please close it before running sync.${NC}"
    exit 1
fi

# 2. Run the Calibre EPUB Engine
echo -e "\n${BLUE}🔄 [1/3] Syncing Calibre E-Book Viewer Highlights...${NC}"
/Applications/calibre.app/Contents/MacOS/calibre-debug -e cali_to_obsidian.py

# 3. Run the Mac Preview PDF Engine
echo -e "\n${BLUE}🔄 [2/3] Syncing macOS Preview PDF Highlights...${NC}"
uv run python3 mac_preview_to_obsidian.py

# 4. Run the Acrobat Reader PDF Engine
echo -e "\n${BLUE}🔄 [3/3] Syncing Acrobat Reader PDF Highlights...${NC}"
uv run python3 adobe_to_obsidian.py

# 5. Success Completion message
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✨ All updates synced perfectly directly into your Grimoire vault!${NC}\n"
else
    echo -e "\n${RED}❌ Synchronization encountered an error during runtime.${NC}\n"
fi

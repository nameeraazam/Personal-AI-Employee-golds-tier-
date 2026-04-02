@echo off
REM Facebook Setup - Quick Guide
REM This will open Facebook and guide you

echo ================================================================
echo   FACEBOOK GRAPH API SETUP - QUICK GUIDE
echo ================================================================
echo.
echo This script will open the required Facebook pages.
echo You need to complete the setup manually.
echo.
echo ================================================================
echo   STEP 1: Create Facebook App
echo ================================================================
echo.
echo Opening Facebook Developers...
start https://developers.facebook.com/apps/
echo.
echo INSTRUCTIONS:
echo 1. Click "Create App"
echo 2. Select "Business" 
echo 3. App Name: Gold Tier FTE Integration
echo 4. Email: Your email
echo 5. Click "Create App"
echo.
pause

echo.
echo ================================================================
echo   STEP 2: Add Permissions
echo ================================================================
echo.
echo Opening Graph API Explorer...
start https://developers.facebook.com/tools/explorer/
echo.
echo INSTRUCTIONS:
echo 1. Select your app from dropdown
echo 2. Click "Add a Permission"
echo 3. Add these 6 permissions ONE BY ONE:
echo.
echo    - pages_show_list
echo    - read_page_mailboxes
echo    - pages_read_engagement
echo    - pages_read_user_content
echo    - pages_manage_posts
echo    - pages_manage_engagement
echo.
pause

echo.
echo ================================================================
echo   STEP 3: Generate Access Token
echo ================================================================
echo.
echo INSTRUCTIONS:
echo 1. Click "Get Token" button
echo 2. Select "Get User Access Token"
echo 3. Check ALL 6 permissions
echo 4. Click "Generate Token"
echo 5. Click "Continue as [Your Name]"
echo 6. Click "Done"
echo.
echo 7. Copy the Access Token that appears
echo.
pause

echo.
echo ================================================================
echo   STEP 4: Get Page ID
echo ================================================================
echo.
echo INSTRUCTIONS:
echo 1. In the query box at top, type: /me/accounts
echo 2. Click "Submit"
echo 3. Copy the "id" value (this is your PAGE ID)
echo 4. Copy the "access_token" value (this is your PAGE TOKEN)
echo.
pause

echo.
echo ================================================================
echo   STEP 5: Get App ID and Secret
echo ================================================================
echo.
echo Opening App Dashboard...
start https://developers.facebook.com/apps/
echo.
echo INSTRUCTIONS:
echo 1. Click on your app
echo 2. Go to Settings → Basic
echo 3. Copy "App ID"
echo 4. Click "Show" next to App Secret and copy it
echo.
pause

echo.
echo ================================================================
echo   STEP 6: Add to .env File
echo ================================================================
echo.
echo Now edit the .env file with your credentials.
echo.
echo Opening .env.example for reference...
notepad .env.example
echo.
echo INSTRUCTIONS:
echo 1. Copy .env.example to .env
echo 2. Edit .env and add:
echo.
echo    FACEBOOK_ACCESS_TOKEN=your_page_token_here
echo    FACEBOOK_PAGE_ID=your_page_id_here
echo    FACEBOOK_APP_ID=your_app_id_here
echo    FACEBOOK_APP_SECRET=your_app_secret_here
echo.
pause

echo.
echo ================================================================
echo   STEP 7: Test Connection
echo ================================================================
echo.
echo Testing Facebook connection...
python integrations\facebook_integration.py --insights
echo.
pause

echo.
echo ================================================================
echo   SETUP COMPLETE!
echo ================================================================
echo.
echo If you see page insights above, you're all set!
echo Now you can run: run_gold_tier.bat
echo.
pause

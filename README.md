# URL Shortener App - Setup Guide
A simple URL shortener that converts long URLs into short ones. When someone clicks the short URL, they get redirected to the original long URL.

## Step 1: Create DynamoDB Table

1. Go to AWS Console → DynamoDB
2. Click "Create table"
3. Table name: `ShortUrls`
4. Partition key: `id` (String)
5. Leave everything else as default
6. Click "Create table"
7. Wait until status shows "Active"

## Step 2: Create Lambda Function

1. Go to AWS Console → Lambda
2. Click "Create function"
3. Choose "Author from scratch"
4. Function name: `url-shortener-function`
5. Runtime: Python 3.13
6. Click on Change default execution role
7. Choose Use existing role
8. Form the existing role list choose `labrole`
9. Leave everything else as default
10. Click "Create function"

### Upload Lambda Code
1. In the Lambda function page, scroll to "Code source"
2. Delete all existing code
3. Copy and paste the entire content of `lambda_function.py`
4. Click "Deploy"

### Enable Function URL
1. In your Lambda function, go to "Configuration" tab
2. Click "Function URL" in the left menu
3. Click "Create function URL"
4. Auth type: NONE
5. Click "Save"
6. **COPY THE FUNCTION URL** - you'll need it in the next step

## Step 3: Update Frontend Code

1. Open `index.html` in a text editor
2. Find this line (line 124):
   ```javascript
        const LAMBDA_FUNCTION_URL = 'https://**********.lambda-url.us-west-2.on.aws/';
   ```
3. Replace `YOUR_LAMBDA_FUNCTION_URL_HERE` with your actual Lambda Function URL
4. Save the file

## Step 4: Create S3 Bucket for Website

1. Go to AWS Console → S3
2. Click "Create bucket"
3. Bucket name: Choose a unique name (e.g., `my-url-shortener-app-123`)
4. choose "ACLs enabled"
5. **UNCHECK** "Block all public access"
6. Check the acknowledgment box
7. Enable Bucket Versioning
8. Click "Create bucket"

### Set Bucket Policy
1. Go to "Permissions" tab
2. Scroll to "Bucket policy"
3. Click "Edit"
4. Paste this policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-url-shortener-app-123/*"
        }
    ]
}
```
5. Click "Save changes"

### Configure Static Website Hosting
1. Click on your bucket name
2. Go to "Properties" tab
3. Scroll to "Static website hosting"
4. Click "Edit"
5. Enable static website hosting
6. Index document: `index.html`
7. Click "Save changes"

### Upload Your HTML File
1. Go to "Objects" tab
2. Click "Upload"
3. Add your updated `index.html` file
4. in the permission section choose "grant public read access"
5. Check the acknowledgment box
6. Click "Upload"

## Step 5: Get Your Website URL

1. In your S3 bucket, go to "Properties" tab
2. Scroll to "Static website hosting"
3. Copy the "Bucket website endpoint" URL
4. This is your website URL!

## Step 6: Test Your App

1. Open your website URL in a browser
2. Enter a long URL (e.g., `https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html`)
3. Click "Shorten URL"
4. You should get a short URL
5. Click the short URL to test redirection

## Testing URLs

Try these URLs to test your shortener:
- `https://www.google.com`
- `https://github.com`
- `https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html`

## That's It!
Your URL shortener should now be working. The short URLs will look like:
`https://your-lambda-url.lambda-url.region.on.aws/abc123`



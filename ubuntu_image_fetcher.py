import requests
import os
import hashlib
from urllib.parse import urlparse
from pathlib import Path


class UbuntuImageFetcher:
    def __init__(self):
        self.download_dir = "Fetched_Images"
        self.downloaded_hashes = set()
        self.load_existing_hashes()

    def load_existing_hashes(self):
        """Load hashes of already downloaded images to prevent duplicates"""
        if os.path.exists(self.download_dir):
            for file in os.listdir(self.download_dir):
                filepath = os.path.join(self.download_dir, file)
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                            self.downloaded_hashes.add(file_hash)
                    except:
                        continue

    def get_file_hash(self, content):
        """Calculate MD5 hash of file content"""
        return hashlib.md5(content).hexdigest()

    def is_duplicate(self, content):
        """Check if image content is already downloaded"""
        content_hash = self.get_file_hash(content)
        return content_hash in self.downloaded_hashes

    def is_safe_file_type(self, response):
        """Check if the file type is safe to download"""
        content_type = response.headers.get('content-type', '').lower()
        safe_types = [
            'image/jpeg', 'image/jpg', 'image/png',
            'image/gif', 'image/webp', 'image/bmp'
        ]

        # Check content type header
        if content_type and not any(st in content_type for st in safe_types):
            return False

        # Additional safety: check file extension from URL
        url = response.url
        safe_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        file_extension = os.path.splitext(urlparse(url).path)[1].lower()

        if file_extension and file_extension not in safe_extensions:
            return False

        return True

    def get_filename_from_url(self, url, response):
        """Extract filename from URL or generate one based on content type"""
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        if not filename or '.' not in filename:
            # Generate filename based on content type
            content_type = response.headers.get('content-type', 'image/jpeg')
            if 'jpeg' in content_type or 'jpg' in content_type:
                extension = '.jpg'
            elif 'png' in content_type:
                extension = '.png'
            elif 'gif' in content_type:
                extension = '.gif'
            elif 'webp' in content_type:
                extension = '.webp'
            else:
                extension = '.jpg'  # default

            filename = f"downloaded_image{extension}"

        return filename

    def download_single_image(self, url):
        """Download a single image from URL"""
        try:
            print(f"\nConnecting to: {url}")

            # Create headers to mimic a real browser
            headers = {
                'User-Agent': 'UbuntuImageFetcher/1.0 (Community Image Collector)',
                'Accept': 'image/jpeg,image/png,image/gif,image/webp,*/*'
            }

            # Fetch the image with timeout
            response = requests.get(
                url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()  # Raise exception for bad status codes

            # Check important HTTP headers
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                print("✗ File too large. Maximum size is 10MB.")
                return False

            # Check if file type is safe
            if not self.is_safe_file_type(response):
                print("✗ File type not supported or potentially unsafe.")
                return False

            # Read content
            content = response.content

            # Check for duplicates
            if self.is_duplicate(content):
                print("✓ Image already exists in collection (duplicate prevented)")
                return True

            # Get appropriate filename
            filename = self.get_filename_from_url(url, response)
            filepath = os.path.join(self.download_dir, filename)

            # Ensure unique filename
            counter = 1
            base_name, extension = os.path.splitext(filename)
            while os.path.exists(filepath):
                filename = f"{base_name}_{counter}{extension}"
                filepath = os.path.join(self.download_dir, filename)
                counter += 1

            # Save the image
            with open(filepath, 'wb') as f:
                f.write(content)

            # Add to downloaded hashes
            self.downloaded_hashes.add(self.get_file_hash(content))

            print(f"✓ Successfully fetched: {filename}")
            print(f"✓ Image saved to {filepath}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
            return False
        except Exception as e:
            print(f"✗ An error occurred: {e}")
            return False

    def download_multiple_images(self, urls):
        """Download multiple images from a list of URLs"""
        successful_downloads = 0

        for i, url in enumerate(urls, 1):
            print(f"\n--- Processing image {i}/{len(urls)} ---")
            url = url.strip()
            if url:  # Skip empty URLs
                if self.download_single_image(url):
                    successful_downloads += 1

        return successful_downloads


def main():
    print("=" * 60)
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web")
    print("=" * 60)

    fetcher = UbuntuImageFetcher()

    # Create directory if it doesn't exist
    os.makedirs(fetcher.download_dir, exist_ok=True)

    while True:
        print("\nHow would you like to proceed?")
        print("1. Download a single image")
        print("2. Download multiple images")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == '1':
            url = input("\nPlease enter the image URL: ").strip()
            if url:
                fetcher.download_single_image(url)
                print("\nConnection strengthened. Community enriched.")
            else:
                print("✗ No URL provided.")

        elif choice == '2':
            print("\nEnter multiple URLs (one per line). Press Enter twice when done:")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)

            if urls:
                successful = fetcher.download_multiple_images(urls)
                print(
                    f"\n✓ Successfully downloaded {successful}/{len(urls)} images")
                print("Community connections multiplied. Wisdom shared.")
            else:
                print("✗ No URLs provided.")

        elif choice == '3':
            print("\nThank you for using Ubuntu Image Fetcher.")
            print("Go forth and share in the spirit of Ubuntu!")
            break

        else:
            print("✗ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()

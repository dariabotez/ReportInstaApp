from instagram_private_api import (
    Client, ClientCompatPatch, ClientError, ClientLoginRequiredError
)

# Defining Insta credentials
IG_USERNAME = 'micca_lorenn'
IG_PASSWORD = ''

# Authenticate Insta account
try:
    ig = Client(IG_USERNAME, IG_PASSWORD)
    ig.login()
except ClientError as e:
    if e.code == 'checkpoint_challenge_required':
        # Two-factor authentication is required
        challenge_url = e.error_response.get('checkpoint_url')
        if not challenge_url:
            print('Failed to get challenge URL')
            exit()
        # Send a GET request to the challenge URL to retrieve a CSRF token
        headers = {'Referer': challenge_url}
        response = ig.session.get(challenge_url, headers=headers, allow_redirects=True)
        csrf_token = response.cookies.get('csrftoken')
        if not csrf_token:
            print('Failed to get CSRF token')
            exit()
        # Prompt the user to enter the verification code
        verification_code = input('Enter the verification code sent to your email or phone number: ')
        # Send a POST request with the verification code and CSRF token to complete the login process
        headers = {'Referer': challenge_url, 'X-CSRFToken': csrf_token}
        data = {'security_code': verification_code}
        response = ig.session.post(challenge_url, headers=headers, data=data, allow_redirects=True)
        if response.status_code == 200:
            ig.login()
        else:
            print('Failed to complete two-factor authentication')
            exit()
    else:
        print(f'Failed to authenticate Instagram account: {e}')
        exit()

# Get the list of users you're following on Instagram
following = []
next_max_id = True
rank_token = ig.generate_uuid()
while next_max_id:
    # If next_max_id is True, it means that this is the first call
    # If next_max_id is a string (for example, "abcdef123456"), it means that we're continuing from the last call
    if next_max_id is True:
        next_max_id = ''
    # Get the list of users you're following on Instagram
    results = ig.user_following(ig.authenticated_user_id, rank_token, max_id=next_max_id)
    # Add the results to the list of users you're following
    following.extend(results.get('users', []))
    # Set next_max_id to the ID of the next page of results, or to None if there are no more results
    next_max_id = results.get('next_max_id')

# Get the list of users who follow you on Instagram
followers = []
next_max_id = True
while next_max_id:
    # If next_max_id is True, it means that this is the first call
    # If next_max_id is a string (for example, "abcdef123456"), it means that we're continuing from the last call
    if next_max_id is True:
        next_max_id = ''
    # Get the list of users who follow you on Instagram
    results = ig.user_followers(ig.authenticated_user_id, rank_token, max_id=next_max_id)
    # Add the results to the list of users who follow you
    followers.extend(results.get('users', []))
    # Set next_max_id to the ID of the next page of results, or to None if there are no more results
    next_max_id = results.get('next_max_id')

# Find the users who follow you and whom you follow back
mutuals = []
for user in followers:
    if user in following:
        mutuals.append(user)

# Find the users who don't follow you back
not_following_back = []
for user in following:
    if user not in mutuals:
        not_following_back.append(user)

# Print the list of users who don't follow you back
print("The following users don't follow you back:")
for user in not_following_back:
    print(user.get('username'))


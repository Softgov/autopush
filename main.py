import git
import schedule
import time

TARGET_BRANCH = 'origin/development'
PATH_TO_SRC_REPO = '../github1'
PATH_TO_DEST_REPO = '../github2'

ORIGINAL_NAME = 'Ivan'
ORIGINAL_EMAIL = 'ivan@almazov.ru'

NEW_NAME = 'pin'
NEW_EMAIL = 'pin@moscow.ru'

ORIGINAL_REMOTE_REPO = 'origin'
NEW_REMOTE_REPO = 'origin2'

# repo.heads.development.commit - последний локальный коммит

def get_last_commit():
    repo = git.Repo(PATH_TO_SRC_REPO)
    for remote in repo.remotes:
        branches = remote.fetch()
        for branch in branches:
            if branch.name == TARGET_BRANCH:
                with open('last_commit.txt', 'r') as f:
                    last_commit = f.read()
                if branch.commit.hexsha == last_commit:
                    print('No changes')
                else:
                    with open('last_commit.txt', 'w') as f:
                        f.write(branch.commit.hexsha)
                    print(f'There are changes, new commit: {branch.commit.hexsha}')

if __name__ == '__main__':
    schedule.every(10).seconds.do(get_last_commit)
    while True:
        schedule.run_pending()
        time.sleep(1)
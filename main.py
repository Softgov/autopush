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
                    print('Set new COMMITTER and AUTHOR')
                    change_commiter(ORIGINAL_EMAIL, NEW_NAME, NEW_EMAIL)
                    print('git push...')
                    push_to_different_repo()
                    print('Set original COMMITTER and AUTHOR')
                    change_commiter(NEW_EMAIL, ORIGINAL_NAME, ORIGINAL_EMAIL)   


def change_commiter(old_email, new_name, new_email):
    git.Repo(PATH_TO_SRC_REPO).git.execute(['git', 'filter-branch', '-f', '--env-filter',
                f'OLD_EMAIL="{old_email}" CORRECT_NAME="{new_name}" CORRECT_EMAIL="{new_email}" \n' +
                'if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ] \n' +
                'then \n' +
                    'export GIT_COMMITTER_NAME="$CORRECT_NAME" \n' +
                    'export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL" \n' +
                'fi \n' +
                'if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ] \n' +
                'then ' +
                    'export GIT_AUTHOR_NAME="$CORRECT_NAME" \n' +
                    'export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL" \n' +
                ' fi', '--tag-name-filter', 'cat', '--', '--branches', '--tags'])

def push_to_different_repo():

    dest_remote_repo = git.Repo(PATH_TO_DEST_REPO).config_reader().get_value(f'remote "{ORIGINAL_REMOTE_REPO}"', "url")

    git.Repo(PATH_TO_SRC_REPO).create_remote(NEW_REMOTE_REPO, dest_remote_repo)

    # branch = TARGET_BRANCH.split('/')[1]

    # git.Repo(PATH_TO_SRC_REPO).remote(name=NEW_REMOTE).push(f'{commit_hexsha}:{branch}')

    git.Repo(PATH_TO_SRC_REPO).git.execute(['git', 'push', '-f', NEW_REMOTE_REPO, 'refs/heads/*'])

    git.Repo(PATH_TO_SRC_REPO).delete_remote(git.Repo(PATH_TO_SRC_REPO).remote(NEW_REMOTE_REPO))

    git.Repo(PATH_TO_SRC_REPO).git.execute(['git', 'pull', ORIGINAL_REMOTE_REPO, '--allow-unrelated-histories'])

if __name__ == '__main__':
    schedule.every(10).seconds.do(get_last_commit)
    while True:
        schedule.run_pending()
        time.sleep(1)
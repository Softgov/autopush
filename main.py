import git
import schedule
import time
import configparser

config = configparser.ConfigParser()
config.read('config')

TARGET_BRANCH = config['SETTINGS']['target_branch']
PATH_TO_DEV_REPO = config['SETTINGS']['path_to_dev_repo']
PATH_TO_PROD_REPO = config['SETTINGS']['path_to_prod_repo']

DEV_REPO_NAME = config['SETTINGS']['dev_repo_name']
DEV_REPO_EMAIL = config['SETTINGS']['dev_repo_email']

PROD_REPO_NAME = config['SETTINGS']['prod_repo_name']
PROD_REPO_EMAIL = config['SETTINGS']['prod_repo_email']

NEW_NAME = config['SETTINGS']['new_name']
NEW_EMAIL = config['SETTINGS']['new_email']

ORIGINAL_REMOTE_REPO = config['SETTINGS']['original_remote_repo']
NEW_REMOTE_REPO = config['SETTINGS']['new_remote_repo']

# repo.heads.development.commit - последний локальный коммит

def get_last_commit(path_to_src_repo, path_to_dest_repo, target_branch, original_name, original_email, new_name, new_email, commit_file):
    repo = git.Repo(path_to_src_repo)
    for remote in repo.remotes:
        branches = remote.fetch()
        for branch in branches:
            if branch.name == target_branch:
                with open(commit_file, 'r') as f:
                    last_commit = f.read()
                print(branch.commit.message)
                if branch.commit.hexsha == last_commit:
                    print(f' Repo {path_to_src_repo} has no changes')
                    repo.git.execute(['git', 'pull', ORIGINAL_REMOTE_REPO, '--allow-unrelated-histories'])
                else:
                    with open(commit_file, 'w') as f:
                        f.write(branch.commit.hexsha)
                    print(f'There are changes in repo {path_to_src_repo}, new commit: {branch.commit.hexsha}')
                    print('Set new COMMITTER and AUTHOR')
                    change_commiter(path_to_src_repo, original_email, new_name, new_email)
                    print('git push...')
                    push_to_different_repo(path_to_src_repo, path_to_dest_repo)
                    print('Set original COMMITTER and AUTHOR')
                    change_commiter(path_to_src_repo, new_email, original_name, original_email)   


def change_commiter(path_to_repo, old_email, new_name, new_email):
    git.Repo(path_to_repo).git.execute(['git', 'filter-branch', '-f', '--env-filter',
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

def push_to_different_repo(path_to_src_repo, path_to_dest_repo):

    dest_remote_repo = git.Repo(path_to_dest_repo).config_reader().get_value(f'remote "{ORIGINAL_REMOTE_REPO}"', "url")

    git.Repo(path_to_src_repo).create_remote(NEW_REMOTE_REPO, dest_remote_repo)

    # branch = TARGET_BRANCH.split('/')[1]

    # git.Repo(PATH_TO_SRC_REPO).remote(name=NEW_REMOTE).push(f'{commit_hexsha}:{branch}')

    git.Repo(path_to_src_repo).git.execute(['git', 'push', '-f', NEW_REMOTE_REPO, 'refs/heads/*'])

    git.Repo(path_to_src_repo).delete_remote(git.Repo(path_to_src_repo).remote(NEW_REMOTE_REPO))

    git.Repo(path_to_src_repo).git.execute(['git', 'pull', ORIGINAL_REMOTE_REPO, '--allow-unrelated-histories'])

if __name__ == '__main__':
    schedule.every(10).seconds.do(get_last_commit, path_to_src_repo=PATH_TO_DEV_REPO, path_to_dest_repo=PATH_TO_PROD_REPO, target_branch=TARGET_BRANCH, original_name=DEV_REPO_NAME, original_email=DEV_REPO_EMAIL, new_name=NEW_NAME, new_email=NEW_EMAIL, commit_file='last_commit_dev.txt')
    schedule.every(15).seconds.do(get_last_commit, path_to_src_repo=PATH_TO_PROD_REPO, path_to_dest_repo=PATH_TO_DEV_REPO, target_branch=TARGET_BRANCH, original_name=PROD_REPO_NAME, original_email=PROD_REPO_EMAIL, new_name=NEW_NAME, new_email=NEW_EMAIL, commit_file='last_commit_prod.txt')
    while True:
        schedule.run_pending()
        time.sleep(1)

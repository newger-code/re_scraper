import git from 'git-last-commit';

const lastCommit = () => new Promise((resolve, reject) => {
  git.getLastCommit((err, commit) => {
    if (err) reject(err);
    else resolve(commit);
  });
});

export default {
  lastCommit
};
const path = require('path');

module.exports = {
  chainWebpack: config => {
      config.module.rules.delete('eslint');
  },

  pages: {
      index: {
          entry: 'src/pages/index/main.ts',
          template: 'public/loading_index.html',
          filename: 'index.html',
          title: 'HV Battle Log'
      },
  },

  configureWebpack: {
    resolve: {
        extensions: ['.ts', '.vue', '.json'],
        alias: {
          '@': path.resolve('src'),
        }
      },
  }
}
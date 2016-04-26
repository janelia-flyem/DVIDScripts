module.exports = {
  context: __dirname + "/src",
  entry: "./root",
  output: {
    path: __dirname,
    filename: "bundle.js"
  },
  module: {
    loaders: [{
      test: /\.jsx?$/,
      loader: 'babel-loader',
      exclude: /node_modules/,
      query: {
        presets: ['es2015', 'react']
      }
    },
    {
      test: /node_modules\/.+\.(jsx|js)$/,
      loader: 'imports?jQuery=jquery,$=jquery,this=>window'
    }
    ]
  }
}

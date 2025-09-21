# depo_fe

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
npm run dev -- --host 127.0.0.1 --port 5175
```

### Compile and Minify for Production

```sh
npm run build
```

### Compile and Minify for Production

lsof -nP -iTCP:5175 -sTCP:LISTEN //Узнать PID
kill <PID> //Остановить

module.exports = {
  apps: [
    {
      name: "reiltor_server",
      script: "daphne",
      args: "-b 0.0.0.0 -p 8000 --application-close-timeout 60 --proxy-headers reiltor.asgi:application",
      interpreter: "python3",
      watch: true,
      max_restarts: 100,
      exp_backoff_restart: 100,
    },
  ],
};

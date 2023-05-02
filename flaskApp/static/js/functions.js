const redirectPage = (htmlId, new_url) => {
  $(htmlId).on("click", function () {
    $.ajax({
      type: "POST",
      url: "http://ysjcs.net:5014/redirectPage",
      async: true,
      dataType: "json",
      data: JSON.stringify({
        new_url: new_url,
      }),
      contentType: "application/json",
    })
      .done(function (result) {
        window.location.href = result.new_url;
      })
      .fail(function (jqXHR, errorThrown) {
        if (jqXHR.status === 401) {
          swal({
            title: "Error!",
            text: jqXHR.statusText,
            icon: "error",
            button: null,
          });
          setTimeout(() => {
            window.location.href = "/login";
          }, 2000);
        } else {
          swal({
            title: "Error!",
            text: errorThrown,
            icon: "error",
            button: "OK",
          });
        }
      });
  });
};

const generate_yt_page = (type) => {
  $(document).ready(function () {
    $("#spinner").show();
    redirectPage("#arrow", "/home");
    $.ajax({
      url: "http://ysjcs.net:5014/get_API_KEY",
      method: "GET",
      async: true,
      dataType: "json",
    }).done(function (result) {
      const apiKey = result.API_KEY;
      $.ajax({
        url:
          "https://www.googleapis.com/youtube/v3/search?key=" +
          apiKey +
          `&type=video&part=snippet&maxResults=50&q=${type}workout`,
        method: "GET",
        dataType: "json",
        async: true,
      })
        .done(function (result) {
          $("#spinner").hide();
          for (i = 0; i < result.items.length; i++) {
            $("#video-item-wrapper").append(
              `<div class="video-item" id="video-item-${result.items[i].id.videoId}" itemId = ${result.items[i].id.videoId}>` +
                `<a href="https://www.youtube.com/watch?v=${result.items[i].id.videoId}"><div class="video">` +
                `<img src="${result.items[i].snippet.thumbnails.high.url}" alt="video" class="thumbnail"/>` +
                "</div></a>" +
                `<p class="video-title">${result.items[i].snippet.title}</p>` +
                '<div class="add-container"><button class="add-btn" id="add-btn"> add to favourite </button></div>' +
                "</div>"
            );
          }
        })
        .fail(function (jqXHR, errorThrown) {
          if (jqXHR.status === 401) {
            $("#spinner").hide();
            swal({
              title: "Error!",
              text: jqXHR.statusText,
              icon: "error",
              button: null,
            });
            setTimeout(() => {
              window.location.href = "/login";
            }, 2000);
          } else {
            $("#spinner").hide();
            swal({
              title: "Error!",
              text: errorThrown,
              icon: "error",
              button: "OK",
            });
          }
        });

      $(document).on("click", "#add-btn", function (e) {
        $("#spinner").show();
        const itemId = $(this).closest(".video-item").attr("itemId");
        const videoId = {
          video_id: itemId,
        };
        $.ajax({
          type: "POST",
          url: "http://ysjcs.net:5014/addFavourite",
          async: true,
          dataType: "json",
          data: JSON.stringify(videoId),
          contentType: "application/json",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        })
          .done(function (result) {
            $("#spinner").hide();
            swal({
              title: "Success",
              text: result.message,
              icon: "success",
              button: "OK",
            });
          })
          .fail(function (jqXHR) {
            if (jqXHR.status === 401) {
              $("#spinner").hide();
              swal({
                title: "Error!",
                text: jqXHR.statusText,
                icon: "error",
                button: null,
              });
              setTimeout(() => {
                window.location.href = "/login";
              }, 2000);
            } else {
              $("#spinner").hide();
              swal({
                title: "Error!",
                text: jqXHR.responseJSON.message,
                icon: "error",
                button: "OK",
              });
            }
          });
      });
    });
  });
};

const generate_myWorkout_page = (
  workout_type,
  exercise_name,
  reps,
  sets,
  kg,
  btn
) => {
  $(document).ready(function () {
    let isEditing = false;
    $("#spinner").show();
    redirectPage("#arrow", "/myworkout");
    const info = {
      type: workout_type,
    };
    $.ajax({
      method: "POST",
      url: "http://ysjcs.net:5014/getMyWorkout",
      dataType: "json",
      contentType: "application/json",
      data: JSON.stringify(info),
      async: true,
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
    })
      .done(function (result) {
        $("#spinner").hide();
        for (i = 0; i < result.length; i++) {
          const result_id = result[i][0];
          const result_name = result[i][1];
          const result_sets = result[i][2];
          const result_reps = result[i][3];
          const result_kg = result[i][4];

          const workoutItemHtml = `
    <div class="workout-item" id="${result_id}" >
      <div class="workout-item-left">
        <div class="workout-item-left-name">
          <p>${result_name}</p>
        </div>
        <div class="workout-item-left-stats">
          <p>${result_reps} reps</p>
          <p>${result_sets} sets</p>
          <p>${result_kg}kg</p>
        </div>
      </div>
      <div class="workout-item-right">
        <img src="../static/images/edit.svg" alt="edit-icon" id="edit" />
        <img src="../static/images/delete-bin.svg" alt="bin" id="bin" />
      </div>
    </div>
  `;

          $(".workout-item-wrapper").append(workoutItemHtml);
        }
      })
      .fail(function (jqXHR, errorThrown) {
        if (jqXHR.status === 401) {
          $("#spinner").hide();
          swal({
            title: "Error!",
            text: jqXHR.statusText,
            icon: "error",
            button: null,
          });
          setTimeout(() => {
            window.location.href = "/login";
          }, 2000);
        } else {
          $("#spinner").hide();
          swal({
            title: "Error!",
            text: errorThrown,
            icon: "error",
            button: "OK",
          });
        }
      });

    $(".addExercise").on("submit", function (e) {
      if (isEditing === false) {
        $("#spinner").show();
        e.preventDefault();
        const exerciseInfo = {
          exercise_name: $("#exercise-name").val(),
          sets: $("#sets").val(),
          reps: $("#reps").val(),
          kg: $("#kg").val(),
          type: workout_type,
        };
        $.ajax({
          type: "POST",
          url: "http://ysjcs.net:5014/saveMyWorkout",
          dataType: "json",
          async: true,
          contentType: "application/json",
          data: JSON.stringify(exerciseInfo),
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        })
          .done(function () {
            $("#spinner").hide();
            $("#exercise-name").val("");
            $("#sets").val("");
            $("#reps").val("");
            $("#kg").val("");
            swal({
              title: "Success",
              text: "Added successfully",
              icon: "success",
              button: null,
            });
            setTimeout(() => {
              window.location.reload();
            }, 2000);
          })
          .fail(function (jqXHR) {
            if (jqXHR.status === 401) {
              $("#spinner").hide();
              swal({
                title: "Error!",
                text: jqXHR.statusText,
                icon: "error",
                button: null,
              });
              setTimeout(() => {
                window.location.href = "/login";
              }, 2000);
            } else {
              $("#spinner").hide();
              swal({
                title: "Error!",
                text: jqXHR.responseJSON.error,
                icon: "error",
                button: "OK",
              });
            }
          });
      }
    });

    $(document).on("click", "#bin", function () {
      const workoutItemId = $(this).closest(".workout-item").attr("id");
      swal({
        title: "Are you sure?",
        text: "Once deleted, you will not be able to recover this item!",
        icon: "warning",
        buttons: true,
        dangerMode: true,
      }).then((confirmDelete) => {
        if (confirmDelete) {
          $("#spinner").show();
          const workoutInfo = {
            workout_id: workoutItemId,
            type: workout_type,
          };
          $.ajax({
            type: "POST",
            url: "http://ysjcs.net:5014/deleteMyWorkout",
            async: true,
            dataType: "json",
            data: JSON.stringify(workoutInfo),
            contentType: "application/json",
            headers: {
              Authorization: "Bearer " + localStorage.getItem("token"),
            },
          })
            .done(function () {
              $("#spinner").hide();
              swal({
                title: "Success",
                text: "Deleting item....",
                icon: "success",
                button: null,
              });
              setTimeout(() => {
                window.location.reload();
              }, 2000);
            })
            .fail(function (jqXHR, errorThrown) {
              if (jqXHR.status === 401) {
                $("#spinner").hide();
                swal({
                  title: "Error!",
                  text: jqXHR.statusText,
                  icon: "error",
                  button: null,
                });
                setTimeout(() => {
                  window.location.href = "/login";
                }, 2000);
              } else {
                $("#spinner").hide();
                swal({
                  title: "Error!",
                  text: errorThrown,
                  icon: "error",
                  button: "OK",
                });
              }
            });
        }
      });
    });

    $(document).on("click", "#edit", function () {
      isEditing = true;
      const workoutItemId = $(this).closest(".workout-item").attr("id");
      const info = {
        workout_id: workoutItemId,
        type: workout_type,
      };
      $.ajax({
        method: "POST",
        url: "http://ysjcs.net:5014/getSpecificWorkout",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(info),
        async: true,
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
      })
        .done(function (result) {
          const result_name = result[0][1];
          const result_reps = result[0][2];
          const result_sets = result[0][3];
          const result_kg = result[0][4];

          $(exercise_name).val(result_name);
          $(reps).val(result_reps);
          $(sets).val(result_sets);
          $(kg).val(result_kg);
          $(btn).text("Save");
          $(btn).attr("id", "edit-btn");

          $(document).on("click", "#edit-btn", function (e) {
            if (isEditing === true) {
              e.preventDefault();
              const workout_info = {
                workout_id: workoutItemId,
                type: workout_type,
                workout_name: $("#exercise-name").val(),
                workout_reps: $("#reps").val(),
                workout_sets: $("#sets").val(),
                workout_kg: $("#kg").val(),
              };
              $.ajax({
                method: "POST",
                url: "http://ysjcs.net:5014/editMyWorkout",
                dataType: "json",
                contentType: "application/json",
                data: JSON.stringify(workout_info),
                async: true,
                headers: {
                  Authorization: "Bearer " + localStorage.getItem("token"),
                },
              })
                .done(function () {
                  $(exercise_name).val("");
                  $(reps).val("");
                  $(sets).val("");
                  $(kg).val("");
                  $(btn).text("Add Exercise");
                  isEditing = false;
                  swal({
                    title: "Success",
                    text: "Edited successfully",
                    icon: "success",
                    button: null,
                  });
                  setTimeout(() => {
                    window.location.reload();
                  }, 2000);
                })
                .fail(function (jqXHR, errorThrown) {
                  if (jqXHR.status === 401) {
                    $("#spinner").hide();
                    swal({
                      title: "Error!",
                      text: jqXHR.statusText,
                      icon: "error",
                      button: null,
                    });
                    setTimeout(() => {
                      window.location.href = "/login";
                    }, 2000);
                  } else {
                    $("#spinner").hide();
                    console.log(jqXHR);
                    swal({
                      title: "Error!",
                      text: errorThrown,
                      icon: "error",
                      button: "OK",
                    });
                  }
                });
            }
          });
        })
        .fail(function (jqXHR, errorThrown) {
          if (jqXHR.status === 401) {
            $("#spinner").hide();
            swal({
              title: "Error!",
              text: jqXHR.statusText,
              icon: "error",
              button: null,
            });
            setTimeout(() => {
              window.location.href = "/login";
            }, 2000);
          } else {
            $("#spinner").hide();
            swal({
              title: "Error!",
              text: errorThrown,
              icon: "error",
              button: "OK",
            });
          }
        });
    });
  });
};

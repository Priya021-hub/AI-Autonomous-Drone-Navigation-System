import { useEffect, useState } from "react"

function App() {

  const [data, setData] = useState({

    message: "Loading...",

    object: "None",

    danger: "LOW",

    direction: "SAFE",

    action: "MOVE FORWARD",

    path: []

  })

const [lastDanger, setLastDanger] = useState("")

const [lastAction, setLastAction] = useState("")

const speak = (text) => {

  window.speechSynthesis.cancel()

  const speech = new SpeechSynthesisUtterance(text)

  speech.rate = 1

  speech.pitch = 1

  speech.volume = 1

  window.speechSynthesis.speak(speech)

}

  // =====================================
  // FETCH LIVE DATA EVERY SECOND
  // =====================================

  useEffect(() => {

    const interval = setInterval(() => {

      fetch("http://127.0.0.1:8000")

        .then((response) => response.json())

        .then((result) => {

          console.log(result)

          setData(result)

        })

        .catch((error) => {

          console.log(error)

        })

    }, 1000)

    return () => clearInterval(interval)

  }, [])

useEffect(() => {

  if (data.danger !== lastDanger) {

    if (data.danger === "HIGH") {

      speak("Warning. Obstacle ahead")

    }

    else if (data.danger === "MEDIUM") {

      speak("Caution. Object detected")

    }

    else if (data.danger === "LOW") {

      speak("Path is clear")

    }

    setLastDanger(data.danger)

  }

}, [data.danger])

useEffect(() => {

  if (data.action !== lastAction) {

    setTimeout(() => {

      if (data.action === "MOVE LEFT") {
        speak("Move left")
      }

      else if (data.action === "MOVE RIGHT") {
        speak("Move right")
      }

      else if (data.action === "STOP") {
        speak("Stop")
      }

    }, 300)

    setLastAction(data.action)
  }

}, [data.action])


  return (

    <div
      style={{
        backgroundColor: "#0f172a",
        minHeight: "100vh",
        color: "white",
        padding: "20px",
        fontFamily: "Arial"
      }}
    >

      {/* TITLE */}

      <h1
        style={{
          textAlign: "center",
          fontSize: "45px",
          marginBottom: "30px",
          color: "#38bdf8"
        }}
      >
        AI Autonomous Drone Navigation System
      </h1>

      {/* GRID */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px"
        }}
      >

        {/* LIVE CAMERA */}

        <div
          style={{
            backgroundColor: "#1e293b",
            padding: "20px",
            borderRadius: "15px",
            boxShadow: "0 0 10px rgba(0,0,0,0.4)"
          }}
        >

          <h2
            style={{
              textAlign: "center"
            }}
          >
            Live Camera Feed
          </h2>

          <img
            src="http://127.0.0.1:8000/video"
            alt="Live Video"
            style={{
              width: "100%",
              borderRadius: "10px",
              marginTop: "10px"
            }}
          />

        </div>

        {/* LIVE DETECTION */}

        <div
          style={{
            backgroundColor: "#1e293b",
            padding: "20px",
            borderRadius: "15px",
            boxShadow: "0 0 10px rgba(0,0,0,0.4)"
          }}
        >

          <h2
            style={{
              textAlign: "center"
            }}
          >
            Live AI Detection
          </h2>

          <div
            style={{
              marginTop: "20px",
              fontSize: "22px",
              lineHeight: "45px"
            }}
          >

            <p>
              <strong>Status:</strong> {data.message}
            </p>

            <p>
              <strong>Object:</strong> {data.object}
            </p>

            <p>
              <strong>Danger:</strong> {data.danger}
            </p>

            <p>
              <strong>Direction:</strong> {data.direction}
            </p>

            <p>
              <strong>Action:</strong> {data.action}
            </p>

<p>
  <strong>Obstacles:</strong> {data.obstacle_count}
</p>

          </div>

        </div>

        {/* PATH PLANNING */}

        {/* PATH PLANNING */}

        <div
          style={{
            backgroundColor: "#1e293b",
            padding: "20px",
            borderRadius: "15px",
            boxShadow: "0 0 10px rgba(0,0,0,0.4)"
          }}
        >
          <h2 style={{ textAlign: "center" }}>
            A* Path Planning
          </h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(20, 20px)",
              gap: "2px",
              justifyContent: "center",
              marginTop: "20px"
            }}
          >
            {data.grid &&
              data.grid.flatMap((row, y) =>
                row.map((cell, x) => {
                  const isPath =
                    data.path &&
                    data.path.some(([px, py]) => px === x && py === y)

                  return (
                    <div
                      key={`${x}-${y}`}
                      style={{
                        width: "20px",
                        height: "20px",
                        border: "1px solid #111",
                        backgroundColor:
                          isPath
                            ? "#facc15"
                            : cell === 1
                            ? "#ef4444"
                            : "#22c55e"
                      }}
                    />
                  )
                })
              )}
          </div>
<div
  style={{
    marginTop: "20px",
    maxHeight: "200px",
    overflowY: "auto",
    backgroundColor: "#0f172a",
    padding: "10px",
    borderRadius: "10px"
  }}
>
  <h3>Safe Path Coordinates</h3>

  {data.path && data.path.length > 0 ? (
    <ul style={{ paddingLeft: "20px", color: "#facc15" }}>
      {data.path.map(([x, y], index) => (
        <li key={index}>
          Step {index + 1}: ({x}, {y})
        </li>
      ))}
    </ul>
  ) : (
    <p style={{ color: "#94a3b8" }}>No path found</p>
  )}
</div>
          

          <p>🟩 Free Cell</p>
          <p>🟥 Obstacle</p>
          <p>🟨 Safe Path</p>
        </div>
  


        {/* SYSTEM STATUS */}

        <div
          style={{
            backgroundColor: "#1e293b",
            padding: "20px",
            borderRadius: "15px",
            boxShadow: "0 0 10px rgba(0,0,0,0.4)"
          }}
        >

          <h2
            style={{
              textAlign: "center"
            }}
          >
            System Status
          </h2>

          <div
            style={{
              marginTop: "20px",
              fontSize: "20px",
              lineHeight: "40px",
              textAlign: "center"
            }}
          >

            <p>YOLOv8 Detection Active</p>

            <p>Live Navigation Active</p>

            <p>Obstacle Avoidance Active</p>

            <p>Frontend Connected to FastAPI</p>

            <p>A* Algorithm Running</p>
 <button
    onClick={() => speak("Move left")}
    style={{
      padding: "10px",
      marginTop: "20px"
    }}
  >
    Test Voice
  </button>

          </div>

        </div>

      </div>

    </div>

  )
}

export default App


		
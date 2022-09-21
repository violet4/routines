import useSWR from 'swr';
import './App.css';

const fetcher = (...args) => fetch(...args).then(res => res.json());



function App() {

    const CreateNewActivity = (e) => {
        e.preventDefault();
        console.log(document.getElementById('newActivityName').value);
        const {data, error} = useSWR('/activity', fetcher);
        if (error) return <div>Failed to load</div>;
        if (!data) return <div>loading...</div>;
        console.log('data:', data)
        return <div>Hello {data}</div>
    };

    const Activities = () => {
        const {data, error} = useSWR('/activity', fetcher);
        if (error) return <div>Failed to load</div>;
        if (!data) return <div>loading...</div>;
        console.log('data:', data)
        return <div>Hello {data}</div>
    };

    return (
        <div className="App">
            <form>
                <input
                    id="newActivityName"
                    type="text"
                />
                &nbsp;
                <input
                    type="submit"
                    value="Submit"
                    onClick={(e) => CreateNewActivity(e)}
                />
            </form>
            <Activities />
        </div>
    );
}

export default App;
